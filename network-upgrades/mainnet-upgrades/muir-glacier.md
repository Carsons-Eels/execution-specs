---
eip: 2387
title: "Hardfork Meta: Muir Glacier"
author: James Hancock (@madeoftin)
discussions-to: https://ethereum-magicians.org/t/hard-fork-to-address-the-ice-age-eip-2387
type: Meta
status: Final
created: 2019-11-22
requires: 1679, 2384
legacy link: https://eips.ethereum.org/EIPS/eip-2387
---

## Abstract

This meta-EIP specifies the changes included in the Ethereum hard fork named Muir Glacier. This hard fork addresses the impending Ice Age on Ethereum Mainnet and includes a commitment to solving the problems with the ice age more permanently.

## Motivation

Ethereum achieves a consistent block time due to its' difficulty retargeting algorithm. If a block-time is higher than 20 seconds, it reduces the difficulty, and if a block time is lower than 10 seconds, it increases the difficulty. This mechanism reaches typically an equilibrium of around 13-14 seconds. Included within this mechanism is something we refer to as the Difficulty Bomb or the Ice Age. It artificially adds to the difficulty in such a way that the retargeting mechanism, at some point, can not adapt to the increase, and we see increased block times throughout the network. The ice age increments every 100,000 blocks. It at first is barely noticeable, but once it is visible, there is a drastic effect on block-times in the network.

The primary problem with the Ice Age is that it is included in the complex mechanism that targets block times, which is an entirely separate in purpose. What is worse is due to being intwined with that algorithm, it is very difficult to simulate or predict its effect on the network. To predict the impact of the ice age, you must both make assumptions about the difficulty of main-net in the future, and predict the effect of changes in difficulty to the impact on the ice age and thus block-times.

This fork will push back the Iceage as far as is reasonable and will give us time to update the Iceage to no longer have these design problems. There are two solutions to consider within that time frame.

 - Update the mechanism so that behavior is predictable.
 - Remove the Iceage entirely

## Specification

- Codename: Muir Glacier

### Activation
  - `Block >= 9,200,000` on the Ethereum mainnet
  - `Block >= 7,117,117` on the Ropsten testnet
  - `Block >= N/A` on the Kovan testnet
  - `Block >= N/A` on the Rinkeby testnet
  - `Block >= N/A` on the Görli testnet

### Included EIPs
  - [EIP-2384](https://eips.ethereum.org/EIPS/eip-2384): Istanbul/Berlin Difficulty Bomb Delay

## Rationale

I want to address the rationale for the intention of the Iceage and the implementation of the Iceage separately.

**The original intentions of the ice age include:** 

 - At the time of upgrades, inhibit unintentional growth of the resulting branching forks leading up to Eth 2.0. *
 - Encourage a prompt upgrade schedule for the path to Eth 2.0. *
 - Forces the community to come back into agreement repeatedly...and it gives whatever portion of the community that wants to a chance to fork off
 - Is a check for the Core Devs in the case that a decision is made to freeze the code base of clients without the blessing of the community.

*Note: None of these effects the Freedom to Fork. They are meant to encourage core-devs and the community to upgrade along with the network and prevent the case where sleeper forks remain dormant only later to be resurrected. The requirement for an active fork is to change a client in a way to respond to the ice age. This is in fact what Ethereum Classic has done.
This is not meant to be exhaustive, but the ideas above capture much of what has been written on the original intentions and process of creating the fork. Any additions to this list that need to be made, I am happy to include. Regardless, to effectively implement an updated design for the ice age, all of the intentions need to be revisited and clarified as part of any updates. This clarification will give a clear expectation for the community and core developers moving forward.


**The implementation**

The existing implementation of the ice age, while it does work in practice, is unnecessarily complex to model and confusing to communicate to the community. Any updates to the design should be: 

 - Easy to model the effect on the network
 - Easy to predict when it occurs

This fork would give us time to address the community to understand their priorities better as far as the intentions of the Ice Age, and give time for proposals for better mechanisms to achieve those goals.

### POA Testnets

Muir Glacier never activates on PoA chains – thus will have zero impact on [forkid](https://eips.ethereum.org/EIPS/eip-2124).

### Note on Issuance Reduction

Previous Hardforks to address the Ice Age have also included reductions in the block reward from 5 Eth to 3 Eth to 2 Eth, respectively. In this case, there is no change in issuance, and the block reward remains 2 Eth per block.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
