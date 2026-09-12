include(${CMAKE_CURRENT_LIST_DIR}/../cmake/cpm.cmake)

CPMAddPackage(gtest
  GIT_TAG v1.17.0
  GIT_REPOSITORY https://github.com/google/googletest.git
  OPTIONS
    "INSTALL_GTEST OFF"
)

# XaccInitialisedTests.cpp is in a different core location in the source vs install.
# Add a test to check which one to use.

# Default to core install location
set(XACC_TEST_DIR ${qristal_core_DIR}/tests)
if(EXISTS ${qristal_core_DIR}/tests/misc_cpp)
  # Use core source location instead
  set(XACC_TEST_DIR ${qristal_core_DIR}/tests/misc_cpp)
endif()

# Add tests
add_executable(CITests_decoder
  ${XACC_TEST_DIR}/XaccInitialisedTests.cpp
  ${CMAKE_CURRENT_LIST_DIR}/../tests/SimplifiedDecoderAlgorithm.cpp
  ${CMAKE_CURRENT_LIST_DIR}/../tests/DecoderKernel.cpp
  ${CMAKE_CURRENT_LIST_DIR}/../tests/QuantumDecoderAlgorithm.cpp
  ${CMAKE_CURRENT_LIST_DIR}/../tests/FullDecoderInputValidation.cpp
  ${CMAKE_CURRENT_LIST_DIR}/../tests/CommunityQualification.cpp
)
target_link_libraries(CITests_decoder
  PRIVATE
    qristal::core
    decoder
    simplified_decoder
    GTest::gtest
    GTest::gtest_main
    GTest::gmock
    GTest::gmock_main
)
add_test(NAME ci_tester COMMAND CITests_decoder)

# Dependency-free checks can also be compiled directly without XACC or Docker.
add_executable(decoder_register_validation
  ${CMAKE_CURRENT_LIST_DIR}/../tests/RegisterValidationStandalone.cpp)
target_include_directories(decoder_register_validation PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}/../include)
target_compile_features(decoder_register_validation PRIVATE cxx_std_17)
add_test(NAME decoder_register_validation COMMAND decoder_register_validation)
