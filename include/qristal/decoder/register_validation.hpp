#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace qristal::detail {

inline std::string decoder_score_bits(int score, size_t width) {
  if (width == 0 || width > 30 || score < 0 ||
      static_cast<unsigned int>(score) >= (1u << width))
    throw std::invalid_argument("Decoder score does not fit its register");
  std::string bits(width, '0');
  for (size_t i = 0; i < width; ++i)
    if (static_cast<unsigned int>(score) & (1u << i)) bits[width-1-i] = '1';
  return bits;
}

// Layout used by the full Decoder's existing allocation and precision formulas.
// This checks addressing and dimensions, not the quantum algorithm's correctness.
inline bool valid_decoder_registers(
    size_t steps, size_t alphabet, const std::vector<int>& metric,
    const std::vector<int>& string, const std::vector<int>& nulls,
    const std::vector<int>& repeats, const std::vector<int>& flags,
    const std::vector<int>& total_buffer, const std::vector<int>& beam,
    const std::vector<int>& best, const std::vector<int>& ancilla) {
  if (!steps || steps > static_cast<size_t>(std::numeric_limits<int>::max()) ||
      alphabet < 2 || metric.empty() || string.empty() ||
      metric.size() % steps || string.size() % steps) return false;
  const size_t ml = metric.size() / steps, symbols = string.size() / steps;
  // Scores use signed int throughout the existing implementation.
  if (ml > 30 || symbols > 30 || symbols < std::ceil(std::log2(alphabet))) return false;
  const double ms_value = std::round(0.49999 + std::log2(1 + steps * (std::pow(2, ml) - 1)));
  const double mb_value = std::round(0.49999 + std::log2(1 + std::pow(alphabet, steps) * (std::pow(2, ms_value) - 1)));
  if (!std::isfinite(ms_value) || !std::isfinite(mb_value) ||
      ms_value < ml || ms_value > 30 || mb_value < 1 || mb_value > 30) return false;
  const int64_t ms = ms_value, mb = mb_value, m = ml, s = symbols, l = steps;
  const int64_t p = ms * (ms + 1) / 2;
  const int64_t required = std::max({m+s, ms-m,
      4+5*ms+2*p+ms+s+l*s+l, 4+p+mb+2*ms+l*s+l});
  if (nulls.size() != steps || repeats.size() != steps || flags.size() != steps ||
      total_buffer.size() != static_cast<size_t>(ms-m) ||
      beam.size() != static_cast<size_t>(mb) || best.size() != beam.size() ||
      ancilla.size() < static_cast<size_t>(required)) return false;
  std::set<int> used;
  for (const auto* reg : {&metric, &string, &nulls, &repeats, &flags,
                          &total_buffer, &beam, &best, &ancilla}) {
    for (int bit : *reg) {
      if (bit < 0 || !used.insert(bit).second) return false;
    }
  }
  // execute allocates the sum of register sizes, so gaps/high IDs are unsafe.
  return used.size() <= static_cast<size_t>(std::numeric_limits<int>::max()) &&
         *used.begin() == 0 && static_cast<size_t>(*used.rbegin()) == used.size()-1;
}
}
