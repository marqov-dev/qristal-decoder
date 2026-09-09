// Copyright (c) 2022 Quantum Brilliance Pty Ltd
#include "qristal/decoder/simplified_decoder.hpp"

#include "Algorithm.hpp"
#include "xacc.hpp"
#include "xacc_service.hpp"
#include "xacc_plugin.hpp"
#include <stdexcept>

#include <assert.h>
#include <bitset>
#include <iomanip>
#include <memory>
#include <string>
#include <set>

namespace qristal {

  bool SimplifiedDecoder::initialize(const xacc::HeterogeneousMap &parameters) {

    qpu_ = nullptr;
    owned_qpu_.reset();
    is_msb = false;
    //std::vector<std::vector<float>> probability_table;
    if (!parameters.keyExists<std::vector<std::vector<float>>>("probability_table")) {
        return false;
    }
    probability_table = parameters.get<std::vector<std::vector<float>>>("probability_table");

    //std::vector<int> qubits_string;
    if (!parameters.keyExists<std::vector<int>>("qubits_string")) {
        return false;
    }
    qubits_string = parameters.get<std::vector<int>>("qubits_string");

    // Validate before division/indexing; asserts are disabled in release builds.
    if (probability_table.empty() || qubits_string.empty()) return false;
    const size_t symbols = probability_table.front().size();
    if (symbols < 2 || symbols > 32) return false;
    const size_t bits_per_symbol = static_cast<size_t>(std::ceil(std::log2(symbols)));
    if (qubits_string.size() != probability_table.size() * bits_per_symbol) return false;
    std::set<int> unique_qubits;
    for (int bit : qubits_string) {
      if (bit < 0 || !unique_qubits.insert(bit).second) return false;
    }
    for (const auto& row : probability_table) {
      if (row.size() != symbols) return false;
      double total = 0;
      for (float probability : row) {
        if (!std::isfinite(probability) || probability < 0 || probability > 1) return false;
        total += probability;
      }
      if (std::abs(total - 1.0) > 1e-5) return false;
    }

    nb_timesteps = probability_table.size();
    nq_string = qubits_string.size() ;
    nq_symbol = nq_string/nb_timesteps;
    assert(nb_timesteps*nq_symbol == nq_string);

    //////////////////////////////////////////////////////////////////////////////////////

    //Parameters for comparator oracle in exponential search
    int BestScore = parameters.get_or_default("BestScore", 0);

    qubits_best_score = {};
    if (parameters.keyExists<std::vector<int>>("qubits_best_score")) {
      qubits_best_score = parameters.get<std::vector<int>>("qubits_best_score");
    }

    //////////////////////////////////////////////////////////////////////////////////////

    // Which algorithm to use for the simplified decoder
    method = "ry";
    if (parameters.keyExists<std::string>("method")) {
        method = parameters.get<std::string>("method");
        // Assert that given builder_name is acceptable and
    }

    if (method != "ry") return false;

    //////////////////////////////////////////////////////////////////////////////////////

    //Initialize qpu accelerator
    qpu_ = nullptr;
    if (parameters.stringExists("qpu")) {
      owned_qpu_ = xacc::getAccelerator(parameters.getString("qpu"), {{"shots", 1}});
      qpu_ = owned_qpu_.get();
    } else if (parameters.keyExists<std::shared_ptr<xacc::Accelerator>>("qpu")) {
      owned_qpu_ = parameters.get<std::shared_ptr<xacc::Accelerator>>("qpu");
      qpu_ = owned_qpu_.get();
    } else if (parameters.pointerLikeExists<xacc::Accelerator>("qpu")) {
      qpu_ = parameters.getPointerLike<xacc::Accelerator>("qpu");
    }

    if (!qpu_) {
      owned_qpu_ = xacc::getAccelerator("qpp", {{"shots", 1}});
      qpu_ = owned_qpu_.get();
    }

    if (parameters.keyExists<bool>("is_msb")) {
        is_msb = parameters.get<bool>("is_msb");
    }
    else if (qpu_->name() == "aer") {    // aer qpu has lsb convention
        is_msb = true;
    }


    return true;

  } //SimplifiedDecoder::initialize


  /////////////////////////////////////////////////////////////////////////////////////////////

  const std::vector<std::string> SimplifiedDecoder::requiredParameters() const {
    return {"probability_table", "qubits_string"};
            //"method", "BestScore", "iteration", "qubits_metric", "qubits_beam_metric", "qubits_superfluous_flags",
            //"num_scoring_qubits", "qubits_init_null", "qubits_init_repeat",
            //"qubits_best_score", "qubits_ancilla_oracle", "N_TRIALS"};
  }

  /////////////////////////////////////////////////////////////////////////////////////////////

  void SimplifiedDecoder::execute(
      const std::shared_ptr<xacc::AcceleratorBuffer> buffer) const {

      if (!qpu_) throw std::logic_error("Decoder must be successfully initialized before execution");
      qristal::CircuitBuilder circ;

      const int nq_symbol_const = nq_symbol;

      if ("ry" == method) {
          const xacc::HeterogeneousMap &map = {
              {"probability_table", probability_table},
              {"qubits_string", qubits_string}};

          qristal::RyEncoding build;
          const bool expand_ok = build.expand(map);
          circ.append(build);
      }

      // Measure
      for (int qubit : qubits_string) {
          circ.Measure(qubit);
      }

      // Construct the full circuit including preparation of input trial score
      //std::cout << "\ncirc.get()" << std::endl;
      auto circuit = circ.get();

      // Run circuit
      //std::cout << circuit->toString() << '\n';
      qpu_->execute(buffer, circuit);  // acc
      std::map<std::string, int> measurements = buffer->getMeasurementCounts();
      std::string output_string = buffer->toString() ;

    /////////////////////////////////////////////////////////////////////////////////////////////

    // Normalize backend counts to increasing register order, then write each
    // symbol MSB-first. Collapse adjacent repeated symbols before removing blank.
    const auto f_kernel_ = [&](std::string measured) {
      if (measured.size() != qubits_string.size())
        throw std::runtime_error("Unexpected decoder measurement width");
      if (is_msb) std::reverse(measured.begin(), measured.end());
      const std::string blank(nq_symbol, '0');
      std::string beam, previous;
      for (size_t offset = 0; offset < measured.size(); offset += nq_symbol) {
        auto symbol = measured.substr(offset, nq_symbol);
        std::reverse(symbol.begin(), symbol.end());
        if (symbol != previous && symbol != blank) beam += symbol;
        previous = symbol;
      }
      return beam;
    };
    if (measurements.empty()) throw std::runtime_error("Decoder received no measurements");

      std::map<std::string, int>::iterator iter;
      std::map<std::string, int> beams;
      std::string input_string;
      std::string beam;
      for (iter = measurements.begin(); iter != measurements.end(); iter++){
          input_string = iter->first;
          beam = f_kernel_(input_string);
          if (beams.count(beam) == 0) {
              beams[beam] = 0;
          }

          beams[beam] += iter->second;
      }

      //buffer->addExtraInfo("output_strings", (std::map<std::string, int>) beams);
      std::cout << "max beam:" ;
      auto max_beam_entry = std::max_element(beams.begin(),beams.end(), [](const auto &x, const auto &y){
          return x.second < y.second;
      });
      std::string max_beam = max_beam_entry->first;
      std::cout << max_beam << std::endl;
      buffer->addExtraInfo("best_beam", max_beam);  //->first);
      // Output beams and their shot counts
      int nb_beams = 0;
      for (iter = beams.begin(); iter != beams.end(); iter++ ) {
          std::cout << iter->first << ": " << iter->second << std::endl;
          std::string beam_label = "beam_" + std::to_string(nb_beams);
          buffer->addExtraInfo(beam_label,(std::string) iter->first);
          std::string beam_count_label = "beam_count_" + std::to_string(nb_beams);
          buffer->addExtraInfo(beam_count_label,(int) iter->second);
          nb_beams++;
      }
      buffer->addExtraInfo("nb_beams",nb_beams);


  } // SimplifiedDecoder::execute

}

REGISTER_PLUGIN(qristal::SimplifiedDecoder, xacc::Algorithm)
