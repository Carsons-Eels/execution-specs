from functools import partial
from typing import Dict

import pytest

from ethereum.exceptions import InvalidBlock
from tests.helpers.load_state_tests import (
    Load,
    fetch_state_test_files,
    idfn,
    run_blockchain_st_test,
)

fetch_berlin_tests = partial(fetch_state_test_files, network="Berlin")

FIXTURES_LOADER = Load("Berlin", "berlin")

run_berlin_blockchain_st_tests = partial(
    run_blockchain_st_test, load=FIXTURES_LOADER
)

# Run legacy general state tests
test_dir = "tests/fixtures/BlockchainTests/GeneralStateTests/"

# Every test below takes more than  60s to run and
# hence they've been marked as slow
GENERAL_STATE_SLOW_TESTS = (
    "stTimeConsuming/CALLBlake2f_MaxRounds.json",
    "stTimeConsuming/static_Call50000_sha256.json",
    "vmPerformance/loopExp.json",
    "vmPerformance/loopMul.json",
    "QuadraticComplexitySolidity_CallDataCopy_d0g1v0_Berlin",
    "CALLBlake2f_d9g0v0_Berlin",
    "CALLCODEBlake2f_d9g0v0",
)

# These are tests that are considered to be incorrect,
# Please provide an explanation when adding entries
INCORRECT_UPSTREAM_STATE_TESTS = (
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus. For more details, read:
    # https://github.com/ethereum/py-evm/pull/1224#issuecomment-418775512
    "stRevertTest/RevertInCreateInInit.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stCreate2/RevertInCreateInInitCreate2.json",
    # The test considers a scenario that cannot be reached by following the
    # rules of consensus.
    "stSStoreTest/InitCollision.json",
)

# All tests that recursively create a large number of frames (50000)
BIG_MEMORY_TESTS = ("50000_",)


@pytest.mark.parametrize(
    "test_case",
    fetch_berlin_tests(
        test_dir,
        ignore_list=INCORRECT_UPSTREAM_STATE_TESTS,
        slow_list=GENERAL_STATE_SLOW_TESTS,
        big_memory_list=BIG_MEMORY_TESTS,
    ),
    ids=idfn,
)
def test_general_state_tests(test_case: Dict) -> None:
    try:
        run_berlin_blockchain_st_tests(test_case)
    except KeyError:
        # FIXME: Handle tests that don't have post state
        pytest.xfail(f"{test_case} doesn't have post state")


# Run legacy valid block tests
test_dir = "tests/fixtures/BlockchainTests/ValidBlocks/"

IGNORE_LIST = (
    "bcForkStressTest/ForkStressTest.json",
    "bcGasPricerTest/RPC_API_Test.json",
    "bcMultiChainTest",
    "bcTotalDifficultyTest",
)

# Every test below takes more than  60s to run and
# hence they've been marked as slow
VALID_BLOCKS_SLOW_TESTS = ("bcExploitTest/DelegateCallSpam.json",)


@pytest.mark.parametrize(
    "test_case",
    fetch_berlin_tests(
        test_dir,
        ignore_list=IGNORE_LIST,
        slow_list=VALID_BLOCKS_SLOW_TESTS,
    ),
    ids=idfn,
)
def test_valid_block_tests(test_case: Dict) -> None:
    try:
        run_berlin_blockchain_st_tests(test_case)
    except KeyError:
        # FIXME: Handle tests that don't have post state
        pytest.xfail(f"{test_case} doesn't have post state")


# Run legacy invalid block tests
test_dir = "tests/fixtures/BlockchainTests/InvalidBlocks"

# TODO: Handle once https://github.com/ethereum/tests/issues/1037
# is resolved
# All except GasLimitHigherThan2p63m1_Berlin
xfail_candidates = (
    ("bcUncleHeaderValidity", "timestampTooLow_Berlin"),
    ("bcUncleHeaderValidity", "timestampTooHigh_Berlin"),
    ("bcUncleHeaderValidity", "wrongStateRoot_Berlin"),
    ("bcUncleHeaderValidity", "incorrectUncleTimestamp4_Berlin"),
    ("bcUncleHeaderValidity", "incorrectUncleTimestamp5_Berlin"),
    ("bcUncleSpecialTests", "futureUncleTimestamp3_Berlin"),
    ("bcInvalidHeaderTest", "GasLimitHigherThan2p63m1_Berlin"),
)


def is_in_xfail(test_case: Dict) -> bool:
    for dir, test_key in xfail_candidates:
        if dir in test_case["test_file"] and test_case["test_key"] == test_key:
            return True

    return False


@pytest.mark.parametrize(
    "test_case",
    fetch_berlin_tests(test_dir),
    ids=idfn,
)
def test_invalid_block_tests(test_case: Dict) -> None:
    try:
        # Ideally correct.json should not have been in the InvalidBlocks folder
        if test_case["test_key"] == "correct_Berlin":
            run_berlin_blockchain_st_tests(test_case)
        elif is_in_xfail(test_case):
            # Unclear where this failed requirement comes from
            pytest.xfail()
        else:
            with pytest.raises(InvalidBlock):
                run_berlin_blockchain_st_tests(test_case)
    except KeyError:
        # FIXME: Handle tests that don't have post state
        pytest.xfail(
            "{} doesn't have post state".format(test_case["test_key"])
        )
