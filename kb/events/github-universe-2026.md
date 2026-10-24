---
title: GitHub Universe 2026
softschema:
  contract: paraverse.conference:Event/v2
  schema: ../_schemas/event.schema.yaml
  envelope: event
  status: enforced
event:
  id: event:github-universe-2026
  name: GitHub Universe 2026
  series: GitHub Universe
  edition: '2026'
  organizer: org:github
  start: '2026-10-28T09:00:00-07:00'
  end: '2026-10-29T16:30:00-07:00'
  timezone: America/Los_Angeles
  attendance_modes:
  - in_person
  - virtual
  venue: venue:fort-mason-center
  url: https://githubuniverse.com/
  description: GitHub's global developer event is back. Join the world's fair of software.
  days:
  - id: day:2026-10-26
    date: '2026-10-26'
    label: Pre-event
  - id: day:2026-10-27
    date: '2026-10-27'
    label: Day 0
    access: invitation only
    agenda:
    - start: 08:00
      end: '17:00'
      title: All programming is by invitation only
      description: If you're on the list, we’ll be in touch soon!
  - id: day:2026-10-28
    date: '2026-10-28'
    label: Day 1
    agenda:
    - start: 07:30
      title: Doors open at Fort Mason Center
      description: Pick up your badge, breakfast, and your favorite morning beverage.
    - start: 09:00
      title: Keynote
    - start: '10:00'
      end: '17:30'
      title: Breakout sessions & all experiences open
    - start: '18:00'
      title: Sponsored evening events
      description: Join GitHub and our partners at a selection of evening events.
  - id: day:2026-10-29
    date: '2026-10-29'
    label: Day 2
    agenda:
    - start: 08:00
      title: Doors open at Fort Mason Center
    - start: 09:00
      end: '14:00'
      title: Breakout sessions & all experiences open
    - start: '14:00'
      title: Closing keynote
    - start: '15:00'
      title: Campus closes
      description: It’s not “goodbye” but “see you next year!”
  - id: day:2026-10-30
    date: '2026-10-30'
    label: Day 3
    access: separate ticket required
    agenda:
    - start: 08:00
      end: '16:00'
      title: Day of Learning at GitHub HQ
      description: Join us for a unique experience full of learning and engagement at GitHub Headquarters
        (separate ticket required).
  offers:
  - id: virtual
    name: Virtual
    price: 0.0
    currency: USD
    availability: available
    summary: 'Join the global developer community online: watch the keynote live, gain exclusive access
      to the GitHub Universe Insider Event, and explore even more sessions on demand.'
    includes:
    - Access to streamed keynotes and content
    - Exclusive virtual-only content
    - Full access to recorded sessions once they're available
  - id: in-person
    name: In person
    price: 1399.0
    currency: USD
    availability: sold_out
    summary: Join in person to experience Universe and gain full access to sessions, partner showcases,
      and more.
    includes:
    - Access to keynotes, sessions, panels, and demos
    - Time to get your questions answered by GitHub experts
    - Space to connect with peers
    - A programmable badge
    - Partner booths for interactive demos and practical solutions
    - All day food and drinks. (And donuts, of course!)
    - Access to exclusive merch at The GitHub Shop
  - id: universe-on-the-road
    name: Universe on the road
    price: 0.0
    currency: USD
    availability: application_required
    summary: Universe is hitting the road this year! Join us in a city near you to learn what's new and
      what's next, connect with your local developer community, and experience what makes Universe so
      magical — closer to home.
    includes:
    - Access to keynote, sessions, demos, and customer stories
    - Time to get your questions answered by GitHub experts
    - Space to connect with peers
    - Partner booths for interactive demos and practical solutions
    - Opportunities to deepen your technical skills
  tour_stops:
  - id: sydney
    city: Sydney
    country: Australia
    region: asia-pacific
    date: '2026-11-17'
    venue_name: Sydney Masonic Centre
    registration: open
    url: https://github.registration.goldcast.io/events/66f7c1c9-2dfc-41f2-9924-37db52f9d8d5
  - id: toronto
    city: Toronto
    country: Canada
    region: americas
    date: '2026-11-18'
    venue_name: Design Exchange
    registration: open
    url: https://github.registration.goldcast.io/events/9a12405d-e612-46e3-aad9-a96329cee2da
  - id: paris
    city: Paris
    country: France
    region: emea
    date: '2026-11-30'
    venue_name: Comet Bourse
    registration: open
    url: https://github.registration.goldcast.io/events/3e7cb7c5-8b67-4391-87fd-e6227a1db79a
  - id: bengaluru
    city: Bengaluru
    country: India
    region: asia-pacific
    date: '2026-12-01'
    venue_name: Conrad Bengaluru
    registration: closed
  - id: sao-paulo
    city: São Paulo
    country: Brazil
    region: americas
    date: '2026-12-01'
    venue_name: STATE
    registration: open
    url: https://github.registration.goldcast.io/events/328590a8-5814-4248-ae2e-86acb7664ca8
  - id: madrid
    city: Madrid
    country: Spain
    region: emea
    date: '2026-12-03'
    venue_name: Green Patio
    registration: open
    url: https://github.registration.goldcast.io/events/5cbce871-d753-4e3f-a24a-ffd29eaf7040
  - id: london
    city: London
    country: UK
    region: emea
    date: '2026-12-08'
    venue_name: Convene
    registration: open
    url: https://github.registration.goldcast.io/events/5350e059-cd62-4980-96ea-3a957b981344
  - id: munich
    city: Munich
    country: Germany
    region: emea
    date: '2026-12-10'
    venue_name: Microsoft Office
    registration: open
    url: https://github.registration.goldcast.io/events/bcf4afd7-acee-4c5b-aaf9-480612de389d
  featured_speakers:
  - person:bea-mendez-gandica
  - person:franck-nijhof
  - person:julio-arruda
  - person:cameron-hamilton
  - person:angie-jones
  - person:kent-c-dodds
  - person:jenny-patchen
  - person:john-maeda
  testimonials:
  - GitHub Universe is perfect for advancing your career as a developer. It gives you the knowledge your
    teams need in the rapidly evolving tech world.
  - Universe is very much choose your own adventure based on what matters to you.
  - The relationships that you make at these events are going to pay dividends for the rest of your career.
  sources:
  - system: githubuniverse.com
    url: https://githubuniverse.com/
    retrieved_at: '2026-10-24T06:46:07Z'
    snapshot: raw/site/home.html
  - system: githubuniverse.com
    url: https://githubuniverse.com/pricing
    retrieved_at: '2026-10-24T06:46:07Z'
    snapshot: raw/site/pricing.html
  - system: githubuniverse.com
    url: https://githubuniverse.com/on-the-road
    retrieved_at: '2026-10-24T06:46:08Z'
    snapshot: raw/site/on-the-road.html
---
# GitHub Universe 2026

GitHub's global developer event is back. Join the world's fair of software.

## Days

### Pre-event: 2026-10-26


### Day 0: 2026-10-27 (invitation only)

- 08:00–17:00 All programming is by invitation only

### Day 1: 2026-10-28

- 07:30 Doors open at Fort Mason Center
- 09:00 Keynote
- 10:00–17:30 Breakout sessions & all experiences open
- 18:00 Sponsored evening events

### Day 2: 2026-10-29

- 08:00 Doors open at Fort Mason Center
- 09:00–14:00 Breakout sessions & all experiences open
- 14:00 Closing keynote
- 15:00 Campus closes

### Day 3: 2026-10-30 (separate ticket required)

- 08:00–16:00 Day of Learning at GitHub HQ

## Ways to attend

- **Virtual** (free, available)
- **In person** (1,399 USD, sold out)
- **Universe on the road** (free, application required)

## Universe on the road

- 2026-11-17 Sydney, Australia at Sydney Masonic Centre (registration open)
- 2026-11-18 Toronto, Canada at Design Exchange (registration open)
- 2026-11-30 Paris, France at Comet Bourse (registration open)
- 2026-12-01 Bengaluru, India at Conrad Bengaluru (registration closed)
- 2026-12-01 São Paulo, Brazil at STATE (registration open)
- 2026-12-03 Madrid, Spain at Green Patio (registration open)
- 2026-12-08 London, UK at Convene (registration open)
- 2026-12-10 Munich, Germany at Microsoft Office (registration open)

## Featured speakers

- [Bea Mendez Gandica](../people/bea-mendez-gandica.md)
- [Franck Nijhof](../people/franck-nijhof.md)
- [Julio Arruda](../people/julio-arruda.md)
- [Cameron Hamilton](../people/cameron-hamilton.md)
- [Angie Jones](../people/angie-jones.md)
- [Kent C. Dodds](../people/kent-c-dodds.md)
- [Jenny Patchen](../people/jenny-patchen.md)
- [John Maeda](../people/john-maeda.md)
