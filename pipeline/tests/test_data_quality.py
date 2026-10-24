from __future__ import annotations

from pathlib import Path
from typing import cast

from test_manifests import FakeWeb, ok
from test_profile_sources import SEED, raw_with

from universe_kb.build import OrgRecord, repository_packages
from universe_kb.manifests import verify_package
from universe_kb.models import GitHubAccount, Repository
from universe_kb.people import AccountRegistry
from universe_kb.profile_sources import organization_details
from universe_kb.snapshot import Fetcher


def test_company_details_use_one_domain_verified_page(tmp_path: Path) -> None:
    registry = AccountRegistry()
    for slug in ('acme', 'unrelated'):
        registry.add_social('linkedin', f'company/{slug}', 'org:acme', 'linkedin_profile', SEED)
    raw = raw_with(tmp_path, {'brightdata/linkedin_companies.json': {
        f'https://www.linkedin.com/company/{slug}': {
            'snapshot_id': slug, 'records': [{'name': 'Acme', 'website': website,
                'about': about, 'company_size': size}]}
        for slug, website, about, size in [
            ('acme', 'https://acme.example', 'Acme makes tools.', '51-200 employees'),
            ('unrelated', 'https://other.example', 'An unrelated business.', '2-10 employees')]}})
    records = {'acme': OrgRecord(key='acme', name='Acme', website='https://acme.example')}

    details = organization_details(raw, records, {}, registry)['org:acme']

    assert [d.text for d in details.descriptions] == ['Acme makes tools.']
    assert details.size == 'LinkedIn size range: 51-200 employees'
    assert 'acct:linkedin/company/unrelated' not in registry.accounts


def test_registry_backlink_without_declaration_does_not_verify_publisher() -> None:
    web = FakeWeb({'https://registry.npmjs.org/copied-sample/latest': ok({
        'name': 'copied-sample', 'version': '1.0.0',
        'repository': {'url': 'https://github.com/acme/plugin-samples'}})})

    found = verify_package(cast(Fetcher, web), 'acme/plugin-samples', 'npm', 'copied-sample')

    assert found['verified'] is False


def test_legacy_package_metadata_survives_without_ownership(tmp_path: Path) -> None:
    raw = raw_with(tmp_path, {'packages/repo-packages.json': {'acme/tools': {
        'checked': [{'file': 'package.json', 'status': 200}], 'packages': [{
            'ecosystem': 'npm', 'name': 'acme-tools', 'url': 'https://www.npmjs.com/package/acme-tools',
            'repository_url': 'https://github.com/acme/tools', 'verified': True}]}}})
    repo = Repository.model_construct(id='repo:acme/tools', full_name='acme/tools', owner='gh:acme')
    account = GitHubAccount.model_construct(id='gh:acme', entity='org:acme')
    packages = []

    published = repository_packages(raw, {repo.id: repo}, {account.id: account}, packages)

    assert len(packages) == 1
    assert packages[0].repository_url == 'https://github.com/acme/tools'
    assert packages[0].repository is None
    assert packages[0].publishers == []
    assert not published

    # An explicit, successfully fetched declaration can establish source provenance,
    # while a repository owner still cannot be inferred to be the registry publisher.
    import json

    cached = raw.load("packages/repo-packages.json")
    cached["acme/tools"]["packages"][0]["declared_in"] = "package.json"
    (tmp_path / "packages/repo-packages.json").write_text(json.dumps(cached))
    packages = []
    assert not repository_packages(raw, {repo.id: repo}, {account.id: account}, packages)
    assert packages[0].repository == repo.id
    assert packages[0].publishers == []


def test_catalog_identity_uses_global_name_and_stable_user_ref() -> None:
    from universe_kb.build import listing_keys, person_name
    from universe_kb.people import PeopleIndex

    full = {'userRef': 'u1', 'fullName': 'Ada L.', 'globalFullName': 'Ada Lovelace'}
    short = {'userRef': 'u1', 'fullName': 'A. Lovelace'}
    index = PeopleIndex()
    index.register('person:ada-lovelace', person_name(full), listing_keys(full))

    assert person_name(full) == 'Ada Lovelace'
    assert index.resolve(person_name(short), listing_keys(short), claims_speaking=True) == (
        'person:ada-lovelace')


def test_campus_levels_and_places_do_not_become_external_venues() -> None:
    import yaml

    from universe_kb.build import split_room_label

    curation = yaml.safe_load((Path(__file__).parents[1] / 'curation/venues.yaml').read_text())
    for place, key, note in [
        ('Gateway Pavilion (Level 1)', 'gateway-pavilion', 'Level 1'),
        ('Gateway Pavilion (Level 2)', 'gateway-pavilion', 'Level 2'),
        ('Fort Mason Building A', 'building-a', None),
        ('Fort Mason Building D', 'building-d', None),
        ("General’s Residence", 'generals-residence', None),
        ('Greens', 'building-a', None),
        ('Universe Plaza', 'universe-plaza', None),
    ]:
        assert split_room_label(f'Stage @ {place}', curation) == ('Stage', key, note, None)
    assert split_room_label('Universe Plaza', curation) == (
        'Universe Plaza', 'universe-plaza', None, None)


def test_catalog_placeholder_capacity_is_unknown_in_room_and_slot(tmp_path: Path) -> None:
    from universe_kb.build import OrgIndex, build_rooms, build_session

    raw = raw_with(tmp_path, {'rainfocus/sessions.json': {}, 'rainfocus/rooms.json': {}})
    for value, expected in [('9999', None), ('1000000', None), ('0', None), ('120', 120)]:
        item = {'sessionID': 's1', 'code': 'T1', 'title': 'Tools', 'type': 'Breakout',
                'attributevalues': [], 'times': [{
                    'room': 'Stage', 'roomId': 'r1', 'capacity': value, 'sessionTimeID': 't1',
                    'utcStartTime': '2026/10/28 17:00:00',
                    'utcEndTime': '2026/10/28 18:00:00'}]}
        rooms = build_rooms(raw, [item], {}, {'venues': {}})
        session = build_session(raw, [item], {'s1': 'session:t1'}, {}, {}, rooms,
                                OrgIndex({'organizations': {}}, {}))
        assert next(iter(rooms.values())).capacity == expected
        assert session.slots[0].capacity == expected


def test_rel_me_does_not_assign_project_account_to_site_linker(tmp_path: Path) -> None:
    from test_profile_sources import person

    from universe_kb.build import OrgIndex, link_websites

    owner = person('person:ada', 'Ada Lovelace')
    registry = AccountRegistry()
    registry.add_url('https://project.example', owner.id, 'event_listing', SEED)
    raw = raw_with(tmp_path, {'websites/homepages.json': {'https://project.example': {
        'status': 200, 'rel_me': ['https://x.com/project_team']}}})

    link_websites(raw, registry, {owner.id: owner}, OrgIndex({'organizations': {}}, {}))

    assert 'acct:x/project_team' not in registry.accounts


def test_curated_org_aliases_override_mention_only_names() -> None:
    from universe_kb.build import OrgIndex

    orgs = OrgIndex({'organizations': {'acme': {'name': 'Acme', 'aliases': ['Acme HQ'],
                                              'github': 'acmehq'}}},
                    {'acme': {'name': 'Acme'}})
    assert orgs.ensure('Acme HQ', 'affiliation', SEED) is orgs.ensure('Acme', 'mention', SEED)
    acme = orgs.get('Acme')
    assert acme is not None and acme.github_login == 'acmehq'


def test_catalog_days_use_labels_then_main_program_density(tmp_path: Path) -> None:
    from universe_kb.build import Catalog, catalog_day_labels

    catalog = Catalog('universe25', '2025', 'editions/universe25', current=False)
    raw = raw_with(tmp_path, {f'{catalog.prefix}/sessions.json': {'items': [
        {'times': [{'utcStartTime': '2025/10/28 00:00:00', 'dayDisplayName': 'Day 0'},
                   {'utcStartTime': '2025/10/28 17:00:00', 'dayDisplayName': 'Day 1'},
                   {'utcStartTime': '2025/10/29 17:00:00', 'dayDisplayName': 'Day 2'}]}]}})
    assert catalog_day_labels(raw, catalog, ['2025-10-27', '2025-10-28', '2025-10-29']) == {
        '2025-10-27': 'Day 0', '2025-10-28': 'Day 1', '2025-10-29': 'Day 2'}
    legacy = Catalog('universe23', '2023', 'editions/universe23', current=False)
    raw = raw_with(tmp_path, {f'{legacy.prefix}/sessions.json': {'items': [
        {'times': [{'utcStartTime': f'2023/11/{day} 17:00:00', 'dayDisplayName': 'Wednesday'}]}
        for day, n in [('07', 1), ('08', 8), ('09', 6), ('10', 1)] for _ in range(n)]}})
    assert catalog_day_labels(raw, legacy, ['2023-11-07', '2023-11-08', '2023-11-09',
                                          '2023-11-10']) == {
        '2023-11-07': 'Pre-event', '2023-11-08': 'Day 1', '2023-11-09': 'Day 2',
        '2023-11-10': 'Post-event'}


def test_organization_job_title_words_are_not_company_mentions() -> None:
    from universe_kb.build import Gazetteer

    gazetteer = Gazetteer({'Principal': 'org:principal-financial-group',
                          'Principal Financial Group': 'org:principal-financial-group'})
    assert gazetteer.find('Principal Engineer, Principal Architect, Principal Researcher') == []
    assert gazetteer.find('Principal Financial Group builds software') == [
        ('Principal Financial Group', 'org:principal-financial-group')]


def test_curated_organization_variants_merge_without_conflating_distinct_companies() -> None:
    import yaml

    from universe_kb.build import OrgIndex

    path = Path(__file__).parents[1] / 'curation/organizations.yaml'
    curation = yaml.safe_load(path.read_text())
    orgs = OrgIndex(curation, {})
    for primary, alias in [
        ('Cathay Pacific', 'Cathay Pacific Airlines'),
        ('Cathay Pacific', 'Cathay Pacific airways'),
        ('OTTO', 'Otto GmbH & Co KG'),
        ('OTTO', 'Otto GmbH &Co. KGaA'),
        ('Entire', 'Entire HQ'), ('KPMG US', 'KPMG'),
        ('Principal Financial Group', 'Principal'), ('Pendo.io', 'Pendo'),
        ('Bloomberg LP', 'Bloomberg'), ('VillageSQL', 'villagesql.com'),
    ]:
        assert orgs.key_for(primary) == orgs.key_for(alias)
    assert orgs.key_for('Prudential') != orgs.key_for('Prudential Financial')
    assert orgs.names_for_label('Accenture and Avanade') == ['Accenture', 'Avanade']
    assert orgs.names_for_label('CREATE / University of Washington') == [
        'CREATE', 'University of Washington']
    assert 'Principal' in orgs.ambiguous_mentions


def test_reassigned_catalog_x_profile_is_removed_before_following_links(tmp_path: Path) -> None:
    from test_profile_sources import person

    from universe_kb.models import Source
    from universe_kb.profile_sources import fill_x

    owner = person('person:ada', 'Ada Lovelace')
    registry = AccountRegistry()
    source = Source(system='rainfocus', snapshot='raw/editions/universe23/sessions.json')
    registry.add_social('x', 'old_handle', owner.id, 'event_listing', source)
    raw = raw_with(tmp_path, {'brightdata/x_profiles.json': {'https://x.com/old_handle': {
        'snapshot_id': 'x1', 'records': [{'profile_name': 'Another Person',
            'date_joined': '2025-01-08T00:00:00Z', 'external_link': 'https://unrelated.example'}]}}})

    fill_x(raw, registry, {owner.id: owner})

    assert 'acct:x/old_handle' not in registry.accounts
    assert not registry.websites


def test_curated_company_page_pin_does_not_fall_back_to_another_page(tmp_path: Path) -> None:
    registry = AccountRegistry()
    registry.add_social('linkedin', 'company/other', 'org:acme', 'linkedin_profile', SEED)
    raw = raw_with(tmp_path, {'brightdata/linkedin_companies.json': {
        'https://www.linkedin.com/company/other': {'snapshot_id': 's1', 'records': [
            {'name': 'Acme', 'about': 'Unverified namesake.'}]}}})
    records = {'acme': OrgRecord(key='acme', name='Acme', linkedin='acme')}

    details = organization_details(raw, records, {}, registry)['org:acme']

    assert not details.descriptions
    assert not registry.accounts


def test_enrich_packages_keeps_manifest_provenance(tmp_path: Path) -> None:
    import json

    from universe_kb.enrich import enrich_packages
    from universe_kb.snapshot import Snapshot

    repositories = tmp_path / "kb" / "repositories"
    repositories.mkdir(parents=True)
    (repositories / "tools.yaml").write_text(
        "repository:\n  full_name: acme/tools\n  owner: gh:acme\n"
        "  primary_language: TypeScript\n")
    web = FakeWeb({
        "https://raw.githubusercontent.com/acme/tools/HEAD/package.json":
            ok({"name": "acme-tools"}),
        "https://registry.npmjs.org/acme-tools/latest": ok({
            "name": "acme-tools", "version": "1.0.0",
            "repository": {"url": "https://github.com/acme/tools"}})})
    snapshot = Snapshot(tmp_path / "raw")

    result = enrich_packages(snapshot, cast(Fetcher, web), tmp_path / "kb")

    assert result == {"repositories": 1, "declared": 1, "verified": 1}
    saved = json.loads((snapshot.root / "packages/repo-packages.json").read_text())
    package = saved["acme/tools"]["packages"][0]
    assert package["declared_in"] == "package.json"
    assert package["verified"] is True
