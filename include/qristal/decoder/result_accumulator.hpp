#pragma once

#include <algorithm>
#include <stdexcept>
#include <string>

namespace qristal::detail {

// A non-improving search can pair the old threshold with an unrelated sample.
// Retain a score/string pair only from a strict improvement observation.
class DecoderResult {
  int initial_, score_, trials_ = 0;
  size_t width_;
  bool found_ = false;
  std::string bits_;
public:
  DecoderResult(int initial, size_t width) : initial_(initial), score_(initial), width_(width) {
    if (initial < 0 || width == 0) throw std::invalid_argument("Invalid Decoder result dimensions");
  }
  void observe(int score, const std::string& bits) {
    if (score < 0) throw std::invalid_argument("Negative Decoder result score");
    if (score > score_) {
      if (bits.size() != width_ || !std::all_of(bits.begin(), bits.end(),
          [](char bit) { return bit == '0' || bit == '1'; }))
        throw std::invalid_argument("Malformed improving Decoder result string");
      score_ = score;
      bits_ = bits;
      found_ = true;
    }
    ++trials_;
  }
  int initial() const { return initial_; }
  int score() const { return score_; }
  int trials() const { return trials_; }
  bool found() const { return found_; }
  const std::string& bits() const { return bits_; }
};
}
