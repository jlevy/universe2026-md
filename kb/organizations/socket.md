---
title: Socket
softschema:
  contract: paraverse.conference:Organization/v2
  schema: ../_schemas/organization.schema.yaml
  envelope: organization
  status: enforced
organization:
  id: org:socket
  name: Socket
  roles:
  - affiliation
  description: Socket is a cybersecurity platform that protects companies from software supply chain attacks.
    Companies use Socket to protect their software applications and critical services from malware and
    security threats originating in open source code.
  descriptions:
  - text: Socket is a cybersecurity platform that protects companies from software supply chain attacks.
      Companies use Socket to protect their software applications and critical services from malware and
      security threats originating in open source code.
    basis: linkedin
  tagline: 'Socket is the #1 software supply chain security platform. Next-gen SCA + SBOM + 0-day prevention.
    LOVED BY DEVELOPERS.'
  industry: Computer and Network Security
  size: 'LinkedIn size range: 51-200 employees'
  headquarters: San Francisco
  founded: '2020'
  specialties:
  - Software
  - Security
  - Software supply chain
  - Open source software
  - Application Security
  - Cybersecurity
  - Software Composition Analysis (SCA)
  logo_url: https://media.licdn.com/dms/image/v2/D4E0BAQGYJcW2JHfItA/company-logo_200_200/B4EZ_dgt8HJgAE-/0/1786127769618/socketinc_logo?e=2147483647&v=beta&t=KBiNx77hNEVtG_ymffiF43LsQ6OKKvVJ-ADYZQ4eeTc
  website: https://socket.dev/
  accounts:
  - acct:linkedin/company/socketinc
  locations:
  - San Francisco, US
  updates:
  - text: 'Attackers were stealing secrets from LiteLLM''s GitHub org 11 days before they published the
      malicious litellm 1.107.0 release. Socket ''s Threat Research Team recovered two malicious workflows
      that ran in BerriAI/litellm on October 10 and October 12. Both runs succeeded. Neither left a trace
      in the repo''s normal history. The technique: • Cut a throwaway branch (ci-tmp-<hex>) from a legitimate
      recent commit • Push one commit adding .github/workflows/ cache.yml , titled "ci: bump cache config"
      • Let on: [push] fire in the upstream repo, where secrets resolve to real values • Base64 the secrets,
      POST them to webhook.site , and append || true so the run always reports success • Delete the branch
      the same day The October 10 run took six org-level secrets, including a GitHub token and a GitHub
      App private key. Two days later, a six-job workflow bound five real GitHub Environments to unlock
      their secrets and took 14 more. No overlap with the first set. Reconnaissance, then collection.
      Among the 20 secrets: OpenAI, Anthropic, and Bedrock keys, Postgres and Redis credentials, a GitGuardian
      key for the secret scanner that would surface this activity, and Playwright session state that grants
      Linear access without a password or MFA. Deleting the workflow didn''t erase the evidence. Environment
      deployment records survive. One is still marked Active, deployed from ref ci-tmp-4d8517. Socket
      contacted the LiteLLM team as soon as we found this and coordinated publication with them. LiteLLM
      has since published its own attack-chain investigation. It traces initial access to a key accidentally
      committed to a public repo in May and never revoked, and says its audit logs link the GH_TOKEN stolen
      on October 10 to approval of the October 21 release. Thanks to the LiteLLM team for working with
      us. What we can''t confirm: whether October 10 was the start, whether more cycles ran before October
      21, or whether the collectors received the data. If you run GitHub Actions, check your environment
      deployment history and Actions metrics for workflows you don''t recognize, especially runs from
      branches that no longer exist. Full analysis and IOCs by Socket: https://lnkd.in/egxhpxub'
    date: '2026-10-23T21:58:16Z'
    url: https://www.linkedin.com/posts/socketinc_activity-7519517577182826496-N7ir
    likes: 33
  - text: '🚨 New investigation: Socket found malicious LiteLLM workflows running 11 days before the attack,
      targeting 20 secrets including GitHub, cloud, and AI credentials. After our disclosure, LiteLLM
      linked a stolen token to approval of the malicious release. https://lnkd.in/ecYJAe6r'
    date: '2026-10-23T21:41:57Z'
    url: https://www.linkedin.com/posts/socketinc_new-investigation-socket-found-malicious-activity-7519513470241935361-AXdw
    likes: 10
  - text: Good news, everyone! PHP2Shell exploits are a massive fail (so far) 🤞
    date: '2026-10-23T18:24:23Z'
    url: https://www.linkedin.com/posts/socketinc_good-news-everyone-php2shell-exploits-are-activity-7519463754426916864-7uI1
    likes: 6
  - text: 'Microsoft made TypeScript roughly 10× faster by porting its compiler and tooling to Go. Now
      the VoidZero (acquired by Cloudflare) team is working with the #TypeScript team on tsrs, a Rust
      port reporting up to 8× faster checks than TS 7.0 and ~70% less memory. https://lnkd.in/esq2Tzcr'
    date: '2026-10-23T17:15:34Z'
    url: https://www.linkedin.com/posts/socketinc_typescript-activity-7519446432920047618-Yq80
    likes: 22
  - text: Everything is hacked! eMudhra, PHP, LiteLLM, Node.js , GitLab, Railway, TiDB, QUIC All this
      on an otherwise typical Wednesday in October...
    date: '2026-10-22T15:16:11Z'
    url: https://www.linkedin.com/posts/socketinc_everything-is-hacked-emudhra-php-litellm-activity-7519054002563481600-Hhsl
    likes: 19
  people:
  - person:lelia-bray-musso
  sources:
  - system: brightdata
    url: https://www.linkedin.com/in/le1ia
    record_id: sd_mvm5k44b11nkuuxlmu
    retrieved_at: '2026-10-24T08:51:28Z'
    snapshot: raw/brightdata/linkedin_profiles.json
  - system: brightdata
    url: https://www.linkedin.com/company/socketinc
    record_id: sd_mvm5xmem1d1puu9zcg
    retrieved_at: '2026-10-24T08:56:11Z'
    snapshot: raw/brightdata/linkedin_companies.json
---
# Socket

Website: <https://socket.dev/>

## People

- [Lelia Bray-Musso](../people/lelia-bray-musso.md)
