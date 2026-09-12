#include <qristal/decoder/register_validation.hpp>
#include <qristal/decoder/result_accumulator.hpp>
#include <iostream>
#include <stdexcept>
#include <string>

struct Layout {
  std::vector<std::vector<int>> r;
  Layout() {
    int next = 0;
    for (int size : {6, 2, 2, 2, 2, 1, 6, 6, 53}) {
      std::vector<int> reg;
      for (int i = 0; i < size; ++i) reg.push_back(next++);
      r.push_back(reg);
    }
  }
  bool valid(size_t steps = 2, size_t alphabet = 2) const {
    return qristal::detail::valid_decoder_registers(steps, alphabet,
        r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]);
  }
};

int main() {
  int checks = 0;
  auto check = [&](bool passed, const std::string& name) {
    ++checks;
    if (!passed) throw std::runtime_error(name);
  };
  check(Layout().valid(), "historical layout");
  for (size_t i = 0; i < 9; ++i) {
    Layout missing; missing.r[i].clear();
    check(!missing.valid(), "missing register " + std::to_string(i));
    Layout overlap; overlap.r[i][0] = overlap.r[(i+1)%9][0];
    check(!overlap.valid(), "overlap " + std::to_string(i));
    Layout negative; negative.r[i][0] = -1;
    check(!negative.valid(), "negative " + std::to_string(i));
  }
  Layout gap; gap.r[8].back() = 1000;
  check(!gap.valid(), "qubit beyond allocation");
  Layout short_pool; short_pool.r[8].pop_back();
  check(!short_pool.valid(), "insufficient ancilla");
  Layout fractional; fractional.r[0].pop_back();
  check(!fractional.valid(), "incomplete timestep register");
  check(!Layout().valid(0), "zero timesteps");
  check(!Layout().valid(2, 1), "single symbol");
  check(!Layout().valid(2, 5), "insufficient symbol bits");
  Layout overflow; overflow.r[0].resize(64);
  check(!overflow.valid(), "signed score precision overflow");
  Layout permuted; std::swap(permuted.r[0][0], permuted.r[8][0]);
  check(permuted.valid(), "disjoint dense register permutation");
  check(qristal::detail::decoder_score_bits(0, 6) == "000000", "zero score padding");
  check(qristal::detail::decoder_score_bits(16, 6) == "010000", "score above four bits");
  check(qristal::detail::decoder_score_bits(63, 6) == "111111", "maximum six-bit score");
  for (const auto& sample : std::vector<std::pair<int, size_t>>{{64,6},{-1,6},{0,0},{0,31}}) {
    bool rejected = false;
    try { qristal::detail::decoder_score_bits(sample.first, sample.second); }
    catch (const std::invalid_argument&) { rejected = true; }
    check(rejected, "invalid score/width");
  }
  qristal::detail::DecoderResult result(4, 2);
  result.observe(4, "11");
  check(!result.found() && result.bits().empty(), "threshold is not an observed pair");
  result.observe(7, "01");
  result.observe(5, "10");
  result.observe(7, "11");
  check(result.score() == 7 && result.bits() == "01", "keep original maximum pair");
  result.observe(9, "10");
  check(result.score() == 9 && result.bits() == "10", "replace pair on improvement");
  check(result.trials() == 5 && result.initial() == 4, "trial accounting");
  for (const std::string bits : {"", "1", "000", "1x"}) {
    bool rejected = false;
    try { result.observe(10, bits); } catch (const std::invalid_argument&) { rejected = true; }
    check(rejected && result.score() == 9 && result.bits() == "10" && result.trials() == 5,
          "reject malformed improvement without mutating result");
  }
  qristal::detail::DecoderResult no_improvement(20, 2);
  no_improvement.observe(20, "01");
  no_improvement.observe(19, "10");
  check(!no_improvement.found() && no_improvement.score() == 20 && no_improvement.bits().empty(),
        "high threshold without observed candidate");
  bool negative_rejected = false;
  try { result.observe(-1, "00"); } catch (const std::invalid_argument&) { negative_rejected = true; }
  check(negative_rejected && result.trials() == 5, "negative result score");
  // Reconstruct the number from the comparator's declared register weights.
  for (int threshold = 0; threshold < 64; ++threshold) {
    const auto bits = qristal::detail::decoder_score_register_bits(threshold, 6);
    int prepared = 0;
    for (size_t i = 0; i < bits.size(); ++i)
      if (bits[i] == '1') prepared += 1 << i;
    check(prepared == threshold, "LSB comparator threshold preparation");
    for (int candidate = 0; candidate < 64; ++candidate)
      check((candidate > prepared) == (candidate > threshold), "threshold comparison boundary");
  }
  check(qristal::detail::decoder_score_register_bits(1, 6) == "100000", "lowest bit first");
  check(qristal::detail::decoder_score_register_bits(16, 6) == "000010", "non-palindromic threshold");
  check(qristal::detail::decoder_score_register_bits(1 << 29, 30).back() == '1', "highest supported bit");
  std::cout << "PASS: " << checks << " full Decoder register checks\n";
}
