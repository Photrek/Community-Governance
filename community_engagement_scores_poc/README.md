# Community Engagement Scores (CES)

## Introduction

This project is about calculating so called "engagement scores" for the online community forming around the [Deep Funding](https://deepfunding.ai) initiative of [SingularityNET](https://singularitynet.io). In a first step, a [Proof of Concept (PoC)](https://deepfunding.ai/proposal/community-contribution-scores) software tool has been implemented to immediately help the Deep Funding team with analyzing the social activity on their [proposal portal on Swae](https://proposals.deepfunding.ai). It enables the automatic calculation of engagement scores as well as rewards for community members that are active on the portal, e.g. by creating comments, reactions and ratings. In future iterations of this project, the functionality of the PoC tool will be expanded to cover other tasks that the Deep Funding team is currently handling by manual calculations in spreadsheets.


## Project structure

The implementation of the Proof of Concept tool is divided into three logically distinct parts, which come with their own documentation:

1. [pkg](pkg): A Python package that contains the code for calculating community engagement scores. It can be easily installed and used by **technical users** that have rudimentary experience with Python and its default package manager pip.
2. [app](app): A web app that allows the Deep Funding team to use the functionality of the Python package via a simple GUI. It provides a straightforward way for **non-technical users** to quickly perform calculations that previously were done by hand in complex spreadsheets. This also enables rapid experimentation with different parameters.
3. [server](server) and [Dockerfile](Dockerfile): A web server configuration that provides a default way for deploying the web app. It can be used by **system administrators** to quickly spin up the web app on a local machine or in the cloud within a Docker container.


## References

### Blog by Deep Funding

The [Deep Funding Blog](https://deepfunding.ai/blog/) contains a series of articles that explain the motivation and reasoning behind the idea of calculating community contribution scores. The following is a list of articles and paragraphs that can serve as entry points:

- [2022-03-04: Deep Funding – Introduction](https://deepfunding.ai/deep-funding-supports-teams-and-individuals-to-develop-and-utilize-decentralized-ai)
  - We believe in democracy and decentralized governance. In the proposal, we outlined that Deep Funding will be a community-driven program. This means that the community of token holders will not only give feedback to your proposal but will also ultimately decide which projects will be awarded
- [2022-03-04: Deep Funding and community governance](https://deepfunding.ai/deep-funding-and-community-governance/)
  - All the actions described above take precious time of our community members. We need to make sure that these efforts are rewarded appropriately. It will be a challenge to make this fair and transparent while keeping it as simple as possible. One aspect of this is reputation management. By keeping a log of a person’s constructive contributions, we can estimate and rate their value to the overall system. Based on this ‘reputation score’ we can assign more or less weight to their feedback to projects and other users. Except for weighting their feedback, we can also make reputation a factor in rewards. The longer you have been active, the more effort you put in each round and the better references you get from other users may also impact the rewards you will be given. This is a complex domain, and it will evolve over time.
- [2022-03-04: Deep Funding infrastructure – Tools and processes](https://deepfunding.ai/roadmap-of-the-deep-funding-infrastructure)
  - An important and ongoing topic will be building the right incentives for the community to be active and constructive in the ecosystem.
- [2022-07-05: Round 1 – Voting Analysis Part 2 – improvement options](https://deepfunding.ai/deep-funding-round-1-voting-analysis-part-2)
  - Measure 1: Attracting more voters
  - Measure 2: Creating a better weight-balance between individuals and their token balance
  - Measure 3: Incentivize or give extra weight to voters that display consistent and constructive behavior
- [2022-07-05: Round 1 – Voting analysis part 3 – Next steps](https://deepfunding.ai/voting-analysis-part-3-next-steps)
  - Option 1: Expert reviews
  - Option 2: Incentives for voting
  - Option 3: Forms of liquid democracy
  - Option 4: Reputation ratings
- [2022-09-16: Governance Voting Experiment](https://deepfunding.ai/governance-voting-experiment)
  - Our ultimate goal is to organize Deep Funding as a full community-governed organization, a DAO. This is however a very young field and we approach this transformation process with care. This experiment is a first step in expanding the community’s control beyond voting on the projects and helping us build out the processes and rules that shape Deep Funding. But perhaps even more important, this project is an experiment in governance itself, in the effectiveness of rewards, and the potential of using a ‘reputation score’ that is based on relevant constructive contributions of community members during the process.
- [2022-11-09: Outcomes of Deep Funding Governance Round 1](https://deepfunding.ai/outcomes-of-deep-funding-governance-round-1)
  - Rewards distribution: Based on the calculated reputation ratings, this is the distribution list of the 100,000 AGIX reward tokens.
- [2022-12-14: Deep Funding Round 2 announcement](https://deepfunding.ai/deep-funding-round-2-announcement)
  - Community engagement rewards: In the recent Deep Funding Governance round, we experimented with reputation-based incentives by offering contributors a token reward for their efforts.
- [2023-03-30: Deep Funding round 2 – Results](https://deepfunding.ai/deep-funding-round-2-results)
  - This is the first time that our `voting portal` is supporting both AGIX on Cardano and AGIX on Ethereum. We created a nifty `wallet linking tool` that we expect to be using more often for activities like this. Furthermore, following the successful experiment on our (first) Governance round, we now introduced **Quadratic voting**, and **Reputation-based voting weights** in the Deep Funding round.
- [2023-04-18: Round 2 Voting analysis](https://deepfunding.ai/round-2-voting-analysis)
  - Proposal portal engagement
  - Loyalty rewards
- [2023-08-01: Launching Deep Funding Round 3](https://deepfunding.ai/launching-the-deep-funding-round-3)
  - Community Participation: Calling all interested people! Join our incredible journey of collaboration and brilliance. Beyond commenting and voting on proposals, by being selected, you now have the chance to be part of Peer Reviews, Eligibility Reviews, Milestone Reviews, and managing Surveys from the Awarded Teams. Your participation will be rewarded and it is crucial as we shape the future of SingularityNET together!

### YouTube channel by Deep Funding

The [Deep Funding YouTube channel](https://www.youtube.com/@deepfunding/videos) contains video recordings of regular meetings between the Deep Funding team and community. The following is a list of videos that contain discussions related to community governance topics, including mechanisms for quantifying engagement and distributing rewards:
 
- [Governance Voting Experiment](https://www.youtube.com/watch?v=h14mXSyZZQw)
- [2022-10-05: Community Governance Proposals](https://www.youtube.com/watch?v=LNvRELi9IgA)
- [2022-10-19: Community Governance](https://www.youtube.com/watch?v=kicRTQl3eGQ)
- [SingularityNET + Swae Discussion on DAOs](https://www.youtube.com/watch?v=BQHdu18kz0Q)
- [2022-11-09: Community Governance](https://www.youtube.com/watch?v=cyv70HaSzWg)
- [2022-11-16: Community Governance](https://www.youtube.com/watch?v=Rd3x2M3hWUk)
- [2022-11-23: Community Governance](https://www.youtube.com/watch?v=RRIeiB_361g)
- [2022-12-14: Community Governance](https://www.youtube.com/watch?v=Vgdnq2S10vI)
- [2023-01-11: Community Governance](https://www.youtube.com/watch?v=xVu_bOI7sR8)
- [2023-01-25: Community Governance](https://www.youtube.com/watch?v=lVr9IceXWEo)
- [2023-04-06: Deep Funding Town Hall #6 - Round 2 Voting Results](https://www.youtube.com/watch?v=VtvoDDRo588)
  - Discusses quadratic voting, voting weights from reputation, wallet linking tool, etc.
- [2023-04-28: Community Governance](https://www.youtube.com/watch?v=m_Xwn1YqGfI)
- [2023-06-08: Community Governance](https://www.youtube.com/watch?v=wHjM1jIlBRE)
- [2023-06-22: Community Governance](https://www.youtube.com/watch?v=8RZkGXPFzF4)
  - Introduces new proposal portal by SingularityNET
- [2023-07-06: Community Governance](https://www.youtube.com/watch?v=jdp7vTOmeBM)
- [2023-07-20: Community Governance](https://www.youtube.com/watch?v=_0sRuxOFPEE)
