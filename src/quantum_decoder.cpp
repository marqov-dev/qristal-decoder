// Copyright (c) 2022 Quantum Brilliance Pty Ltd

#include "qristal/decoder/quantum_decoder.hpp"
#include "qristal/decoder/register_validation.hpp"
#include "qristal/decoder/result_accumulator.hpp"
#include <stdexcept>

#include "Algorithm.hpp"
#include "xacc.hpp"
#include "xacc_service.hpp"

#include <assert.h>
#include <iomanip>
#include <memory>

namespace qristal {

  bool QuantumDecoder::initialize(const xacc::HeterogeneousMap &parameters) {

    qpu_ = nullptr;
    owned_qpu_.reset();

    // Validate before indexing rows or dividing by the number of timesteps.
    // These checks must remain active in Release builds (unlike assert).
    if (!parameters.keyExists<int>("iteration") ||
        !parameters.keyExists<std::vector<std::vector<float>>>("probability_table")) {
      return false;
    }
    const auto table =
        parameters.get<std::vector<std::vector<float>>>("probability_table");
    if (table.empty() || table.front().empty()) {
      return false;
    }
    for (const auto &row : table) {
      if (row.size() != table.front().size()) {
        return false;
      }
      double sum = 0.0;
      for (float probability : row) {
        if (!std::isfinite(probability) || probability < 0.0f || probability > 1.0f) {
          return false;
        }
        sum += probability;
      }
      if (std::abs(sum - 1.0) > 1e-5) {
        return false;
      }
    }
    if (!parameters.keyExists<int>("N_TRIALS") ||
        parameters.get<int>("N_TRIALS") <= 0 || parameters.get<int>("iteration") <= 0 ||
        static_cast<size_t>(parameters.get<int>("iteration")) > table.size()) return false;
    if (parameters.key_exists_any_type("method") && !parameters.stringExists("method")) return false;
    method = parameters.stringExists("method") ? parameters.getString("method") : "canonical";
    if (method != "canonical") return false;
    iteration = parameters.get<int>("iteration");
    probability_table = table;

    int alphabet_size = probability_table[0].size();

    //////////////////////////////////////////////////////////////////////////////////////

    //U prime unitary parameters
    qubits_metric = {};
    if (parameters.keyExists<std::vector<int>>("qubits_metric")) {
      qubits_metric = parameters.get<std::vector<int>>("qubits_metric");
    }

    qubits_string = {};
    if (parameters.keyExists<std::vector<int>>("qubits_string")) {
      qubits_string = parameters.get<std::vector<int>>("qubits_string");
    }


    //////////////////////////////////////////////////////////////////////////////////////

    //Parameters for comparator oracle in exponential search
    if (parameters.key_exists_any_type("BestScore") && !parameters.keyExists<int>("BestScore")) return false;
    BestScore = parameters.get_or_default("BestScore", 0);

    qubits_best_score = {};
    if (parameters.keyExists<std::vector<int>>("qubits_best_score")) {
      qubits_best_score = parameters.get<std::vector<int>>("qubits_best_score");
    }

    //////////////////////////////////////////////////////////////////////////////////////

    //Parameters for adder
    qubits_total_metric_buffer = {};
    if (parameters.keyExists<std::vector<int>>("qubits_total_metric_buffer")) {
      qubits_total_metric_buffer =
          parameters.get<std::vector<int>>("qubits_total_metric_buffer");
    }

    //////////////////////////////////////////////////////////////////////////////////////

    //Parameters for exponential search
    N_TRIALS = parameters.get<int>("N_TRIALS");

    //////////////////////////////////////////////////////////////////////////////////////

    // Parameters for decoder kernel
    if (!parameters.keyExists<std::vector<int>>("qubits_init_null")) {
      return false;
    }
    qubits_init_null = parameters.get<std::vector<int>>("qubits_init_null");


    if (!parameters.keyExists<std::vector<int>>("qubits_init_repeat")) {
      return false;
    }
    qubits_init_repeat = parameters.get<std::vector<int>>("qubits_init_repeat");


    qubits_ancilla_pool = {};
    if (parameters.keyExists<std::vector<int>>("qubits_ancilla_pool"))
    {
      qubits_ancilla_pool = parameters.get<std::vector<int>>("qubits_ancilla_pool");
    }

    if (!parameters.keyExists<std::vector<int>>("qubits_superfluous_flags"))
    {
      return false;
    }
    qubits_superfluous_flags = parameters.get<std::vector<int>>("qubits_superfluous_flags");


    qubits_beam_metric = {};
    if (parameters.keyExists<std::vector<int>>("qubits_beam_metric"))
    {
      qubits_beam_metric = parameters.get<std::vector<int>>("qubits_beam_metric");
    }


    //////////////////////////////////////////////////////////////////////////////////////

    if (!detail::valid_decoder_registers(probability_table.size(), alphabet_size,
        qubits_metric, qubits_string, qubits_init_null, qubits_init_repeat,
        qubits_superfluous_flags, qubits_total_metric_buffer, qubits_beam_metric,
        qubits_best_score, qubits_ancilla_pool)) return false;

    if (BestScore < 0 || static_cast<unsigned int>(BestScore) >=
        (1u << qubits_best_score.size())) return false;

    //Initialize qpu accelerator
    qpu_ = nullptr;
    if (parameters.stringExists("qpu")) {
      owned_qpu_ =
          xacc::getAccelerator(parameters.getString("qpu"), {{"shots", 1}});
      qpu_ = owned_qpu_.get();
    } else if (parameters.keyExists<std::shared_ptr<xacc::Accelerator>>("qpu")) {
      owned_qpu_ = parameters.get<std::shared_ptr<xacc::Accelerator>>("qpu");
      qpu_ = owned_qpu_.get();
    } else if (parameters.pointerLikeExists<xacc::Accelerator>("qpu")) {
      qpu_ = parameters.getPointerLike<xacc::Accelerator>("qpu");
    }

    if (!qpu_ && parameters.key_exists_any_type("qpu")) return false;
    if (!qpu_) {
      owned_qpu_ = xacc::getAccelerator("qpp", {{"shots", 1}});
      // Default to qpp if none provided
      qpu_ = owned_qpu_.get();
    }

    return qpu_ != nullptr;
  } //QuantumDecoder::initialize

  /////////////////////////////////////////////////////////////////////////////////////////////

  const std::vector<std::string> QuantumDecoder::requiredParameters() const {
    return {"probability_table", "iteration", "qubits_metric", "qubits_string",
            "method", "BestScore", "qubits_beam_metric", "qubits_superfluous_flags",
            "qubits_init_null", "qubits_init_repeat",
            "qubits_best_score", "qubits_ancilla_pool", "qubits_total_metric_buffer", "N_TRIALS"};
  }

  /////////////////////////////////////////////////////////////////////////////////////////////

  void QuantumDecoder::execute(
      const std::shared_ptr<xacc::AcceleratorBuffer> buffer) const {
    if (!qpu_ || !buffer) throw std::logic_error("Full Decoder requires successful initialization and a result buffer");
    auto gateRegistry = xacc::getService<xacc::IRProvider>("quantum");

    // qubits_next_letter and qubits_next_metric required at the same time
    std::vector<int> qubits_next_letter; // S
    std::vector<int> qubits_next_metric; // m
    int L = probability_table.size();
    int S = qubits_string.size()/L;
    int ml = qubits_metric.size()/L; // letter metric precision
    int ms = std::round(0.49999 + std::log2(1 + L*(std::pow(2,ml) - 1))); // string metric precision
    int p = ms*(ms+1)/2; // number of precision qubits needed for ae for metrics
    int mb = std::round(0.49999 + std::log2(1 + std::pow((int)probability_table[0].size(), L)*(std::pow(2,ms) - 1))); // beam metric precision

    std::cout << "Welcome to the Quantum Decoder!\n";
    std::cout << "----------------------------------------------------------------\n";
    std::cout << "Finding the most likely beam for string length " << L << "and " << probability_table[0].size() << " symbols.\n";
    std::cout << "----------------------------------------------------------------\n";

    int required_num_ancilla = std::max({ml+S, ms-ml, 4+5*ms+2*p+ms+S+L*S+L, 4+p+mb+2*ms+L*S+L});
    if (qubits_ancilla_pool.size() < required_num_ancilla) {
        xacc::error("Not enough ancilla provided.");
    }

    std::cout << "Beginning decoder algorithm.\n";
    for (int i = 0; i < S; i++) {
    qubits_next_letter.push_back(qubits_ancilla_pool[i]);
    }
    for (int i = 0; i < ml; i++) {
    qubits_next_metric.push_back(qubits_ancilla_pool[S+i]);
    }

    // Take the logarithm of the probability table
  //   std::vector<std::vector<float>> log_prob_table;
  //   for (auto i : probability_table) {
  //       std::vector<float> log_i;
  //       for (auto j : i) {
  //           float log_j = std::log2(j);
  //           log_i.push_back(log_j);
  //       }
  //       log_prob_table.push_back(log_i);
  //   }
  //   probability_table = log_prob_table;

    //State preparation: Prepare initial state using unitaries for the exponential search.
    std::function<std::shared_ptr<xacc::CompositeInstruction>(
        std::vector<int>, std::vector<int>, std::vector<int>, std::vector<int>,
        std::vector<int>)>
        state_prep_ = [&](std::vector<int> qubits_string,
                          std::vector<int> qubits_metric,
                          std::vector<int> qubits_next_letter,
                          std::vector<int> qubits_next_metric,
                          std::vector<int> qubits_total_metric_buffer) {
          // Initialize state preparation circuit
          auto gateRegistry = xacc::getService<xacc::IRProvider>("quantum");
          auto state_prep = gateRegistry->createComposite("state_prep");

          /////////////////////////////////////////////////////////////////////////////////////////////

          // Loop over rows of the probability table (i.e. over string length)
          for (int it = 0; it < iteration; it++) {
            // Initialize W prime unitary
            auto w_prime = std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                xacc::getService<xacc::Instruction>("WPrime"));

            // Merge qubit register for W prime unitary into a heterogenous map
            xacc::HeterogeneousMap w_map = {
                {"iteration", it},
                {"qubits_next_letter", qubits_next_letter},
                {"qubits_next_metric", qubits_next_metric},
                {"probability_table", probability_table},
                {"qubits_init_null", qubits_init_null},
                {"flag_integer", 0}};

            // Add qubit register to W prime
            w_prime->expand(w_map);

            // Add W prime unitary to state preparation circuit
            state_prep->addInstruction(w_prime);

            /////////////////////////////////////////////////////////////////////////////////////////////

            // Initialize repetition flags
            if (it > 0) {
              auto init_repeat =
                  std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                      xacc::getService<xacc::Instruction>("InitRepeatFlag"));
              xacc::HeterogeneousMap rep_map = {
                  {"iteration", it},
                  {"qubits_string", qubits_string},
                  {"qubits_next_letter", qubits_next_letter},
                  {"qubits_init_repeat", qubits_init_repeat}};
              init_repeat->expand(rep_map);
              // Add marking of repeat symbols to state preparation circuit
              state_prep->addInstruction(init_repeat);
            }

            /////////////////////////////////////////////////////////////////////////////////////////////

            // Initialize U prime unitary
            auto u_prime = std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                xacc::getService<xacc::Instruction>("UPrime"));

            // Merge qubit register for U prime unitary into a heterogenous map
            xacc::HeterogeneousMap u_map = {
                {"iteration", it},
                {"qubits_next_letter", qubits_next_letter},
                {"qubits_next_metric", qubits_next_metric},
                {"qubits_string", qubits_string},
                {"qubits_metric", qubits_metric}};

            // Add qubit register to U prime
            u_prime->expand(u_map);

            // Add U prime unitary to state preparation circuit
            state_prep->addInstruction(u_prime);

            /////////////////////////////////////////////////////////////////////////////////////////////

            // Initialize Q prime unitary
            auto q_prime = std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                xacc::getService<xacc::Instruction>("QPrime"));

            // Merge qubit register for Q prime unitary into a heterogenous map
            xacc::HeterogeneousMap q_map = {
                {"iteration", it},
                {"qubits_next_letter", qubits_next_letter},
                {"qubits_next_metric", qubits_next_metric},
                {"qubits_string", qubits_string},
                {"qubits_metric", qubits_metric}};

            // Add qubit register to Q prime
            q_prime->expand(q_map);

            // Add Q prime unitary to state preparation circuit
            state_prep->addInstruction(q_prime);
          } // Loop over string length

          /////////////////////////////////////////////////////////////////////////////////////////////

          // The comparator oracle takes in the total metric. Therefore we need to
          // use an adder to sum up the individual scores and form total metric.
          int m = qubits_next_metric
                      .size(); // Size of the qubits_next_metric is constant and
                               // fixed at the initizalization of the program.
          int c_in =
              qubits_ancilla_pool[0]; // qubits_ancilla_adder[0]; //Carry over
          std::vector<int> total_metric;

          // Insert first iteration's qubits into total_metric and use it in the
          // following for-loop to be summed iteratively with other
          // qubits_next_metric iterations
          for (int i = 0; i < m; i++)
            total_metric.push_back(qubits_metric[i]);

          for (int i = 0; i < qubits_total_metric_buffer.size();
               i++) // for (int i = 1; i < qubits_ancilla_adder.size(); i++)
            total_metric.push_back(qubits_total_metric_buffer[i]);

          for (int it = 1; it < iteration; it++) {
            std::vector<int> metrics; // Vector to store elements of the metric at
                                      // each iteration.
            int start = it * m;
            int end = (it + 1) * m;

            for (int i = start; i < end; i++)
              metrics.push_back(qubits_metric[i]);

            for (int i = 0; i < total_metric.size() - 1 - m; i++) {
              metrics.push_back(
                  qubits_ancilla_pool
                      [i + 1]); // metrics.push_back(qubits_ancilla_oracle[i]);
            }

            // Use ripple adder to add the qubits_metric at iteration 'it' to the
            // total metric vector
            auto adder = std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                xacc::getService<xacc::Instruction>("RippleCarryAdder"));
            bool expand_ok = adder->expand({{"adder_bits", metrics},
                                            {"sum_bits", total_metric},
                                            {"c_in", c_in}});
            assert(expand_ok);

            // Add total metric to state preparation circuit
            state_prep->addInstruction(adder);
          }

          /////////////////////////////////////////////////////////////////////////////////////////////

          // Now we apply the decoder kernel to form beam equivalence classes
          std::shared_ptr<xacc::CompositeInstruction> state_prep_clone =
              xacc::ir::asComposite(state_prep->clone());

          auto decoder_kernel =
              std::dynamic_pointer_cast<xacc::CompositeInstruction>(
                  xacc::getService<xacc::Instruction>("DecoderKernel"));
          bool expand_ok = decoder_kernel->expand(
              {{"qubits_string", qubits_string},
               {"qubits_metric", qubits_metric},
               {"qubits_total_metric_buffer", qubits_total_metric_buffer},
               {"qubits_init_null", qubits_init_null},
               {"qubits_init_repeat", qubits_init_repeat},
               {"qubits_superfluous_flags", qubits_superfluous_flags},
               {"qubits_beam_metric", qubits_beam_metric},
               {"qubits_ancilla_pool", qubits_ancilla_pool},
               {"metric_state_prep", state_prep_clone}});
          assert(expand_ok);
          state_prep->addInstruction(decoder_kernel);
          return state_prep;
        };
    auto state_prep_circ =
        state_prep_(qubits_string, qubits_metric, qubits_next_letter,
                    qubits_next_metric, qubits_total_metric_buffer);

    /////////////////////////////////////////////////////////////////////////////////////////////

    // Comparator oracle
    std::function<std::shared_ptr<xacc::CompositeInstruction>(int)> oracle_ =
        [&](int BestScore) {
          int qubit_flag = qubits_ancilla_pool[0];
          int c_in = qubits_ancilla_pool[1];
          int n = qubits_best_score.size();

          // Initialize comparator oracle circuit
          auto oracle = gateRegistry->createComposite("oracle");

          // Encode BestScore as a bitstring
          const std::string BestScore_binary_n = detail::decoder_score_register_bits(BestScore, n);

          // Prepare |BestScore>
          for (int i = 0; i < n; i++) {
            if (BestScore_binary_n[i] == '1') {
              oracle->addInstruction(
                  gateRegistry->createInstruction("X", qubits_best_score[i]));
            }
          }
          // Phase kickback method
          oracle->addInstruction(
              gateRegistry->createInstruction("X", qubit_flag));
          oracle->addInstruction(
              gateRegistry->createInstruction("H", qubit_flag));

          auto comp = std::dynamic_pointer_cast<xacc::CompositeInstruction>(
              xacc::getService<xacc::Instruction>("CompareGT"));
          xacc::HeterogeneousMap options{{"qubits_a", qubits_beam_metric},
                                         {"qubits_b", qubits_best_score},
                                         {"qubit_flag", qubit_flag},
                                         {"qubit_ancilla", c_in},
                                         {"is_LSB", true}};
          const bool expand_ok = comp->expand(options);
          assert(expand_ok);
          oracle->addInstruction(comp);

          oracle->addInstruction(
              gateRegistry->createInstruction("H", qubit_flag));
          oracle->addInstruction(
              gateRegistry->createInstruction("X", qubit_flag));

          return oracle;
        };

    /////////////////////////////////////////////////////////////////////////////////////////////

    //Initiate scoring function
    std::function<int(int)> f_score = [&](int score) { return score; };

    // Validate the success probabilities. This is done by iterating the
    // exponential search N_TRIALS times until the best score is obtained.
    int nSuccess = 0;

    /////////////////////////////////////////////////////////////////////////////////////////////

    //Have to re-initiate total_metric here for getAlgorithm("exponential-search") below
    std::vector<int> total_metric;

    // Insert first iteration's qubits into total_metric and use it in the
    // following for loop to be summed iteratively with other qubits_next_metric
    // iteration
    for (int i = 0; i < ml; i++) {
      total_metric.push_back(qubits_metric[i]);
    }

    for (int i = 0; i < qubits_total_metric_buffer.size(); i++) {
      total_metric.push_back(qubits_total_metric_buffer[i]);
    }

    /////////////////////////////////////////////////////////////////////////////////////////////

    detail::DecoderResult result(BestScore, qubits_string.size());
    int current_best_score = BestScore;
    int total_num_qubits = 3*L + 2*mb + ms - ml + S*L + ml*L + qubits_ancilla_pool.size();

    std::cout<< "Total number qubits = " << total_num_qubits << "\n";

    for (int runCount = 0; runCount < N_TRIALS; ++runCount) {
      std::cout << "Decoder iteration: " << runCount + 1
                << ", initial best score: " << current_best_score << std::endl;

      // for (auto bit : qubits_beam_metric) {
      //     std::cout << "beam metric bit " << bit << "\n";
      // }
      auto exp_search_algo = xacc::getAlgorithm(
        "exponential-search", {{"method", "canonical"},
                               {"state_preparation_circuit", state_prep_circ},
                               {"oracle_circuit", oracle_},
                               {"best_score", current_best_score},
                               {"f_score", f_score},
                               {"total_num_qubits", total_num_qubits},
                               {"qubits_string", qubits_string},
                               {"total_metric", qubits_beam_metric},
                               {"qpu", qpu_}});

      auto trial_buffer = xacc::qalloc(total_num_qubits);
      exp_search_algo->execute(trial_buffer);
      auto info = trial_buffer->getInformation();
      //    std::cout << buffer->toString() << std::endl;
      int bs = info.at("best-score").as<int>();

      // Check the score's declared width, then bind only strict improvements.
      detail::decoder_score_bits(bs, qubits_best_score.size());
      result.observe(bs, info.at("best-string").as<std::string>());
      current_best_score = result.score();
      // if (current_best_score <= previous_best_score && previous_best_score > 0)
      // {
      //   std::cout << std::endl;
      //   std::cout << "--------------------------------------------------" <<
      //   std::endl; std::cout << "Maximum score achieved at decoder iteration "
      //   << runCount
      //             << ", with score: " << previous_best_score
      //             << ", and string: " << best_string << std::endl;
      //   std::cout <<  "Exiting decoder." << std::endl;
      //   std::cout << "--------------------------------------------------" <<
      //   std::endl; std::cout << std::endl; break;
      // }
      std::cout << "--------------------------------------------------"
                << std::endl;
      std::cout << std::endl;
    }
    // Publish only after every trial completed. This is a quantized search
    // observation, not a probability or a certified most-likely decoded beam.
    buffer->addExtraInfo("initial-score", result.initial());
    buffer->addExtraInfo("best-score", result.score());
    buffer->addExtraInfo("best-string", result.bits());
    buffer->addExtraInfo("has-improving-candidate", result.found());
    buffer->addExtraInfo("trials-completed", result.trials());
    buffer->addExtraInfo("method", method);
    buffer->addExtraInfo("result-kind", std::string("quantized-search-observation"));

  } // QuantumDecoder::execute

}
