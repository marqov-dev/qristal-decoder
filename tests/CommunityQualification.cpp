#include <qristal/decoder/simplified_decoder.hpp>
#include <gtest/gtest.h>
#include <limits>

TEST(CommunityQualification, RejectsMalformedInputs) {
  qristal::SimplifiedDecoder decoder;
  auto valid = xacc::HeterogeneousMap{{"probability_table", std::vector<std::vector<float>>{{0, 1}, {1, 0}}}, {"qubits_string", std::vector<int>{0, 1}}};
  EXPECT_FALSE(decoder.initialize({}));
  auto check = [&](std::vector<std::vector<float>> table, std::vector<int> bits) {
    EXPECT_FALSE(decoder.initialize({{"probability_table", table}, {"qubits_string", bits}}));
  };
  check({}, {});
  check({{}}, {0});
  check({{0, 1}, {1}}, {0, 1});
  check({{0, 1}}, {});
  check({{0, 1}, {1, 0}}, {0, 0});
  check({{0, 1}}, {-1});
  check({{-.1f, 1.1f}}, {0});
  check({{.2f, .2f}}, {0});
  check({{std::numeric_limits<float>::quiet_NaN(), 1}}, {0});
  valid.insert("method", std::string("unsupported"));
  EXPECT_FALSE(decoder.initialize(valid));
}

TEST(CommunityQualification, DeterministicCPUBackends) {
  qristal::SimplifiedDecoder decoder;
  for (const auto& backend : {"qpp", "aer", "sparse-sim"}) {
    SCOPED_TRACE(backend);
    auto acc = xacc::getAccelerator(backend, {{"shots", 1024}});
    ASSERT_TRUE(decoder.initialize({
      {"probability_table", std::vector<std::vector<float>>{{0, 1, 0, 0}, {0, 0, 0, 1}}},
      {"qubits_string", std::vector<int>{0, 1, 2, 3}}, {"qpu", acc}}));
    auto buffer = xacc::qalloc(4);
    decoder.execute(buffer);
    auto info = buffer->getInformation();
    EXPECT_EQ(info.at("best_beam").as<std::string>(), "0111");
    EXPECT_EQ(info.at("nb_beams").as<int>(), 1);
    EXPECT_EQ(info.at("beam_count_0").as<int>(), 1024);
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
TEST(CommunityQualification, NamedBackendSelectionIsPerInitialization) {
  for (const std::string name : {"qualification-a", "qualification-b"}) {
    std::shared_ptr<xacc::Accelerator> backend = std::make_shared<RecordingCPU>(name);
    xacc::contributeService(name, backend);
    qristal::SimplifiedDecoder decoder;
    ASSERT_TRUE(decoder.initialize({{"probability_table", std::vector<std::vector<float>>{{0, 1}}}, {"qubits_string", std::vector<int>{0}}, {"qpu", name}}));
    auto buffer = xacc::qalloc(1);
    decoder.execute(buffer);
    EXPECT_EQ(buffer->getInformation().at("qualification_backend").as<std::string>(), name);
  }
}

TEST(CommunityQualification, CollapseRepeatsBeforeRemovingBlanks) {
  for (const auto& backend : {"qpp", "aer", "sparse-sim"}) {
    SCOPED_TRACE(backend);
    for (const auto& symbols : {std::vector<int>{1, 1, 0, 1, 3}, std::vector<int>{0, 0, 0, 0, 0}}) {
      std::vector<std::vector<float>> table;
      for (int symbol : symbols) { std::vector<float> row(4, 0); row[symbol] = 1; table.push_back(row); }
      qristal::SimplifiedDecoder decoder;
      auto acc = xacc::getAccelerator(backend, {{"shots", 128}});
      ASSERT_TRUE(decoder.initialize({{"probability_table", table}, {"qubits_string", std::vector<int>{0,1,2,3,4,5,6,7,8,9}}, {"qpu", acc}}));
      auto buffer = xacc::qalloc(10);
      decoder.execute(buffer);
      EXPECT_EQ(buffer->getInformation().at("best_beam").as<std::string>(), symbols[0] ? "010111" : "");
      EXPECT_EQ(buffer->getInformation().at("beam_count_0").as<int>(), 128);
    }
  }
}
