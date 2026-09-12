#include <qristal/decoder/quantum_decoder.hpp>
#include <gtest/gtest.h>
#include <limits>

// No accelerator is needed: malformed tables must fail before backend lookup.
TEST(FullDecoderInputValidation, RejectsMissingOrWrongTypes) {
  qristal::QuantumDecoder decoder;
  EXPECT_FALSE(decoder.initialize({}));
  EXPECT_FALSE(decoder.initialize({{"iteration", 1}}));
  EXPECT_FALSE(decoder.initialize({{"iteration", 1}, {"probability_table", 7}}));
  EXPECT_FALSE(decoder.initialize({{"iteration", std::string("1")},
      {"probability_table", std::vector<std::vector<float>>{{0.5f, 0.5f}}}}));
}

TEST(FullDecoderInputValidation, RejectsMalformedProbabilityTables) {
  const float nan = std::numeric_limits<float>::quiet_NaN();
  const float inf = std::numeric_limits<float>::infinity();
  const std::vector<std::vector<std::vector<float>>> tables = {
      {}, {{}}, {{0.5f, 0.5f}, {}}, {{0.5f, 0.5f}, {1}},
      {{-0.1f, 1.1f}}, {{nan, 1}}, {{inf, 0}}, {{0, 0}},
      {{0.2f, 0.2f}}, {{0.8f, 0.8f}}};
  for (size_t i = 0; i < tables.size(); ++i) {
    SCOPED_TRACE(i);
    qristal::QuantumDecoder decoder;
    EXPECT_FALSE(decoder.initialize({{"iteration", 1}, {"probability_table", tables[i]}}));
  }
}

namespace {
class RecordingCPU : public xacc::Accelerator {
  std::string label;
public:
  explicit RecordingCPU(std::string value) : label(std::move(value)) {}
  const std::string name() const override { return label; }
  const std::string description() const override { return "qualification routing stub"; }
  void initialize(const xacc::HeterogeneousMap& = {}) override {}
  void updateConfiguration(const xacc::HeterogeneousMap&) override {}
  const std::vector<std::string> configurationKeys() override { return {}; }
  void execute(std::shared_ptr<xacc::AcceleratorBuffer> b, const std::shared_ptr<xacc::CompositeInstruction>) override {
    b->appendMeasurement("1");
    b->addExtraInfo("qualification_backend", label);
  }
  void execute(std::shared_ptr<xacc::AcceleratorBuffer> b, const std::vector<std::shared_ptr<xacc::CompositeInstruction>> c) override { execute(b, c.at(0)); }
};
}

TEST(FullDecoderInputValidation, AcceptsNormalizedTablesWithoutExecuting) {
  std::shared_ptr<xacc::Accelerator> backend = std::make_shared<RecordingCPU>("unused");
  for (const auto &table : std::vector<std::vector<std::vector<float>>>{
      {{0.7f, 0.3f}, {0.2f, 0.8f}}, {{0, 1}, {1, 0}}}) {
    qristal::QuantumDecoder decoder;
    EXPECT_TRUE(decoder.initialize({
        {"iteration", 2}, {"N_TRIALS", 4}, {"probability_table", table},
        {"qubits_metric", std::vector<int>{0,1,2,3,4,5}},
        {"qubits_string", std::vector<int>{6,7}},
        {"qubits_init_null", std::vector<int>{8,9}},
        {"qubits_init_repeat", std::vector<int>{10,11}},
        {"qubits_superfluous_flags", std::vector<int>{12,13}},
        {"qubits_total_metric_buffer", std::vector<int>{14}},
        {"qubits_beam_metric", std::vector<int>{15,16,17,18,19,20}},
        {"qubits_best_score", std::vector<int>{21,22,23,24,25,26}},
        {"qpu", backend}}));
  }
}
