#!/usr/bin/env python3
"""Validate the public AI Film Studio bundle without mutating it."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


EXPECTED_SKILLS = [
    "ai-film-studio",
    "film-wayfinder",
    "production-architect",
    "asset-bible-director",
    "performance-director",
    "visual-development-director",
    "shot-continuity-director",
    "film-prompt-director",
    "iteration-supervisor",
    "post-delivery-director",
    "film-advisor",
]

EXPECTED_INTERFACES = [
    "FilmBrief",
    "ProductionPlan",
    "AssetRecord",
    "ShotRecord",
    "PromptPacket",
    "GenerationAttempt",
    "TaskPacket",
    "AuditPacket",
    "FixPacket",
    "VerificationPacket",
    "DeliveryReceipt",
]

REQUIRED_SCHEMAS = {
    "project-record.schema.json",
    "performance-bible.schema.json",
    "geography-lock.schema.json",
    "iteration-record.schema.json",
    "film-advisor-packet.schema.json",
    "delivery-record.schema.json",
    "FilmBrief.schema.json",
    "ProductionPlan.schema.json",
    "AssetRecord.schema.json",
    "ShotRecord.schema.json",
    "PromptPacket.schema.json",
    "GenerationAttempt.schema.json",
    "TaskPacket.schema.json",
    "AuditPacket.schema.json",
    "FixPacket.schema.json",
    "VerificationPacket.schema.json",
    "DeliveryReceipt.schema.json",
    "ModelProfile.schema.json",
    "ScenarioFixture.schema.json",
}

SOURCE_MARKERS_TO_EXCLUDE = ("HELL GRIND", "CINEDANCE V4", "HIGGSFIELD CREATORS")

REQUIRED_PRACTICAL_TEMPLATES = {
    "character-sheet.md",
    "performance-profile.md",
    "voice-prompt.md",
    "location-map.md",
    "prop-state.md",
    "reference-inheritance.md",
    "scene-block.md",
    "shotlist.md",
    "iteration-log.md",
    "slop-review.md",
    "edit-notes.md",
    "sound-map.md",
    "retrospective.md",
}

REQUIRED_END_TO_END_FIXTURES = {
    "30-second-proof-of-concept.json",
    "dialogue-short.json",
    "simulated-95-minute-feature-plan.json",
}


def load_json(path: Path, errors: List[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path}: invalid JSON: {error}")
        return None


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_value(value: Any, schema: Dict[str, Any], label: str, errors: List[str]) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{label}: expected constant {schema['const']!r}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{label}: expected one of {schema['enum']!r}")
        return

    expected_type = schema.get("type")
    if expected_type and not _type_matches(value, expected_type):
        errors.append(f"{label}: expected {expected_type}")
        return

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{label}: shorter than minimum length")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            errors.append(f"{label}: does not match required pattern")

    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{label}: smaller than minimum")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{label}: fewer than {schema['minItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_value(item, item_schema, f"{label}[{index}]", errors)

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{label}: missing required key {key}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{label}: unexpected key {key}")
        for key, property_schema in properties.items():
            if key in value and isinstance(property_schema, dict):
                validate_value(value[key], property_schema, f"{label}.{key}", errors)


def validate_record_semantics(record: Dict[str, Any], label: str, errors: List[str]) -> None:
    version = record.get("schema_version")
    if version == "ai-film-studio/AssetRecord/v1" and record.get("status") == "approved":
        proof = record.get("proof", {})
        if proof.get("status") != "passed" or not proof.get("evidence_paths"):
            errors.append(f"{label}: approved AssetRecord requires passed proof with evidence")
    elif version == "ai-film-studio/PromptPacket/v1" and record.get("status") == "validated":
        validator = record.get("validator_result", {})
        if not record.get("compiled_prompt") or not re.fullmatch(r"[a-f0-9]{64}", str(record.get("prompt_sha256", ""))):
            errors.append(f"{label}: validated PromptPacket requires compiled prompt and hash")
        if validator.get("status") != "passed" or not validator.get("evidence"):
            errors.append(f"{label}: validated PromptPacket requires passing validator evidence")
    elif version == "ai-film-studio/GenerationAttempt/v1":
        if record.get("status") == "observed" and not record.get("output_references"):
            errors.append(f"{label}: observed GenerationAttempt requires output evidence")
        approval = record.get("approval", {})
        if record.get("status") == "observed" and approval.get("required") and (not approval.get("approval_id") or not approval.get("cost_preview")):
            errors.append(f"{label}: required live action needs approval ID and cost preview")
    elif version == "ai-film-studio/VerificationPacket/v1" and record.get("status") == "passed":
        if not record.get("evidence"):
            errors.append(f"{label}: passed VerificationPacket requires evidence")
    elif version == "ai-film-studio/DeliveryReceipt/v1" and record.get("status") in {"approved_for_external_delivery", "delivered"}:
        delivery = record.get("external_delivery", {})
        if not record.get("final_files") or not record.get("verification_evidence"):
            errors.append(f"{label}: terminal DeliveryReceipt requires final files and verification evidence")
        if not delivery.get("approval_id") or not delivery.get("target"):
            errors.append(f"{label}: terminal DeliveryReceipt requires scoped external approval")


def _relative_path_is_safe(path_value: str) -> bool:
    candidate = Path(path_value)
    return not candidate.is_absolute() and ".." not in candidate.parts


def _read_skill_frontmatter(path: Path, errors: List[str]) -> Dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{path}: cannot read skill: {error}")
        return {}
    if not content.startswith("---\n"):
        errors.append(f"{path}: missing YAML frontmatter")
        return {}
    end = content.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{path}: unterminated YAML frontmatter")
        return {}
    frontmatter: Dict[str, str] = {}
    for line in content[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"')
    if "name" not in frontmatter or "description" not in frontmatter:
        errors.append(f"{path}: frontmatter needs name and description")
    if "Activation: explicit-only" not in content:
        errors.append(f"{path}: missing explicit-only activation declaration")
    return frontmatter


def _load_film_advisor(root: Path):
    module_path = root / "scripts" / "film_advisor.py"
    spec = importlib.util.spec_from_file_location("ai_film_studio_film_advisor", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load film_advisor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_codex_manifest(root: Path, manifest: Dict[str, Any], errors: List[str]) -> None:
    label = ".codex-plugin/plugin.json"
    if manifest.get("name") != "ai-film-studio":
        errors.append(f"{label}: name must be ai-film-studio")
    if manifest.get("version") != "0.2.0":
        errors.append(f"{label}: version must be 0.2.0")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{label}: skills must be ./skills/")
    for prohibited in ("mcpServers", "apps", "hooks"):
        if prohibited in manifest:
            errors.append(f"{label}: {prohibited} must be omitted")
    for companion in (root / ".mcp.json", root / ".app.json", root / "hooks", root / "hooks.json"):
        if companion.exists():
            errors.append(f"{label}: prohibited companion exists: {companion.name}")

    author = manifest.get("author")
    if not isinstance(author, dict) or author.get("name") != "Community Maintainers":
        errors.append(f"{label}: author.name must be Community Maintainers")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{label}: interface must be an object")
        return
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"{label}: interface.{field} must be non-empty")
    if interface.get("developerName") != "Community Maintainers":
        errors.append(f"{label}: interface.developerName must be Community Maintainers")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(isinstance(value, str) and value.strip() for value in capabilities):
        errors.append(f"{label}: interface.capabilities must be non-empty strings")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts or not all(isinstance(value, str) and value.strip() for value in prompts):
        errors.append(f"{label}: interface.defaultPrompt must be a non-empty string list")
    elif len(prompts) > 3:
        errors.append(f"{label}: interface.defaultPrompt may have at most three entries")
    if (root / "plugin.json").exists():
        errors.append("legacy top-level plugin.json must not exist")


def _validate_claude_manifest(root: Path, codex: Dict[str, Any], errors: List[str]) -> None:
    label = ".claude-plugin/plugin.json"
    manifest = load_json(root / ".claude-plugin" / "plugin.json", errors)
    if not isinstance(manifest, dict):
        return
    for field in ("name", "version", "description"):
        if manifest.get(field) != codex.get(field):
            errors.append(f"{label}: {field} must match the Codex manifest")
    if manifest.get("author", {}).get("name") != "Community Maintainers":
        errors.append(f"{label}: author.name must be Community Maintainers")
    if not isinstance(manifest.get("keywords"), list) or not manifest["keywords"]:
        errors.append(f"{label}: keywords must be a non-empty list")


def _validate_plugin_contract(root: Path, contract: Dict[str, Any], errors: List[str]) -> None:
    if contract.get("name") != "ai-film-studio" or contract.get("version") != "0.2.0":
        errors.append("plugin-contract.json: plugin identity mismatch")
    if contract.get("visibility") != "public" or contract.get("publish") is not True:
        errors.append("plugin-contract.json: plugin must be public and publishable")

    activation = contract.get("activation")
    expected_activation = {
        "mode": "explicit-only",
        "implicit_activation": False,
        "activate_on_quoted_name": False,
        "activate_on_negated_name": False,
        "activate_on_conditional_name": False,
        "activate_on_incidental_film_language": False,
    }
    if not isinstance(activation, dict):
        errors.append("plugin-contract.json: activation must be an object")
    else:
        for key, expected in expected_activation.items():
            if activation.get(key) != expected:
                errors.append(f"plugin-contract.json: activation.{key} must be {expected!r}")

    skills = contract.get("skills")
    if skills != EXPECTED_SKILLS:
        errors.append("plugin-contract.json: expected exactly the ordered 11 owned skills")
        return
    for name in skills:
        skill_path = root / "skills" / name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"plugin-contract.json: missing skill file for {name}")
            continue
        frontmatter = _read_skill_frontmatter(skill_path, errors)
        if frontmatter.get("name") != name:
            errors.append(f"skills/{name}/SKILL.md: frontmatter name must match contract")
        agent_path = skill_path.parent / "agents" / "openai.yaml"
        if not agent_path.is_file():
            errors.append(f"skills/{name}: missing explicit-only agent policy")
        else:
            content = agent_path.read_text(encoding="utf-8")
            if "allow_implicit_invocation: false" not in content:
                errors.append(f"skills/{name}: implicit invocation must be disabled")
    if contract.get("record_interfaces") != "schemas/stable-record-interfaces.json":
        errors.append("plugin-contract.json: stable record interface index mismatch")
    composition = contract.get("capability_composition", {})
    local_core = composition.get("local_core", {}) if isinstance(composition, dict) else {}
    optional = composition.get("optional_companions", {}) if isinstance(composition, dict) else {}
    expected_local = {
        "grill_and_wayfinder": "ai-film-studio:film-wayfinder",
        "outcome_contracts": "ai-film-studio:ai-film-studio",
        "prompt_packet": "ai-film-studio:film-prompt-director",
        "runtime_planner": "ai-film-studio:film-advisor",
    }
    if local_core != expected_local:
        errors.append("plugin-contract.json: complete local capability owners are missing")
    if optional.get("model_specific_prompt_format") != "video-production-studio:video-prompt-builder":
        errors.append("plugin-contract.json: optional prompt formatter owner mismatch")
    validation = contract.get("validation", {})
    if not isinstance(validation, dict) or validation.get("bundle") != "python3 scripts/validate_bundle.py .":
        errors.append("plugin-contract.json: package-relative bundle validator is required")
    if ("/" + "Users" + "/") in json.dumps(validation):
        errors.append("plugin-contract.json: validation commands must not contain a personal absolute path")


def _validate_json_records(root: Path, errors: List[str]) -> Dict[str, Dict[str, Any]]:
    schemas_dir = root / "schemas"
    found_schemas = {path.name for path in schemas_dir.glob("*.schema.json")}
    missing = REQUIRED_SCHEMAS - found_schemas
    if missing:
        errors.append(f"schemas: missing {sorted(missing)}")

    schema_by_version: Dict[str, Dict[str, Any]] = {}
    for schema_path in sorted(schemas_dir.glob("*.schema.json")):
        schema = load_json(schema_path, errors)
        if not isinstance(schema, dict):
            continue
        version = schema.get("properties", {}).get("schema_version", {}).get("const")
        if not isinstance(version, str):
            errors.append(f"{schema_path}: schema_version constant missing")
            continue
        schema_by_version[version] = schema

    for group in ("templates", "fixtures/valid"):
        directory = root / group
        for record_path in sorted(directory.glob("*.json")):
            record = load_json(record_path, errors)
            if not isinstance(record, dict):
                continue
            version = record.get("schema_version")
            schema = schema_by_version.get(version)
            if schema is None:
                errors.append(f"{record_path}: unknown schema_version {version!r}")
                continue
            validate_value(record, schema, str(record_path.relative_to(root)), errors)
            validate_record_semantics(record, str(record_path.relative_to(root)), errors)
    return schema_by_version


def _validate_stable_interfaces(
    root: Path, schema_by_version: Dict[str, Dict[str, Any]], errors: List[str]
) -> None:
    index = load_json(root / "schemas" / "stable-record-interfaces.json", errors)
    if not isinstance(index, dict):
        return
    if index.get("interface_version") != "ai-film-studio/stable-record-interfaces/v1":
        errors.append("stable-record-interfaces.json: interface version mismatch")
    interfaces = index.get("interfaces")
    if not isinstance(interfaces, list):
        errors.append("stable-record-interfaces.json: interfaces must be a list")
        return
    names = [item.get("name") for item in interfaces if isinstance(item, dict)]
    if names != EXPECTED_INTERFACES:
        errors.append("stable-record-interfaces.json: interface names or order mismatch")
    for item in interfaces:
        if not isinstance(item, dict):
            errors.append("stable-record-interfaces.json: interface entry must be an object")
            continue
        name = item.get("name")
        for key in ("schema", "template", "fixture"):
            raw_path = item.get(key)
            if not isinstance(raw_path, str) or not _relative_path_is_safe(raw_path):
                errors.append(f"stable-record-interfaces.json: unsafe {key} path for {name}")
                continue
            resolved = root / raw_path
            if not resolved.is_file():
                errors.append(f"stable-record-interfaces.json: missing {key} for {name}")
        schema_path = root / item.get("schema", "")
        template_path = root / item.get("template", "")
        fixture_path = root / item.get("fixture", "")
        schema = load_json(schema_path, errors) if schema_path.is_file() else None
        if not isinstance(schema, dict):
            continue
        if schema.get("title") != name:
            errors.append(f"{schema_path.relative_to(root)}: title must be {name}")
        version = schema.get("properties", {}).get("schema_version", {}).get("const")
        if not isinstance(version, str) or version not in schema_by_version:
            errors.append(f"{schema_path.relative_to(root)}: unregistered schema version")
            continue
        for record_path in (template_path, fixture_path):
            if not record_path.is_file():
                continue
            record = load_json(record_path, errors)
            if isinstance(record, dict):
                validate_value(record, schema, str(record_path.relative_to(root)), errors)
                validate_record_semantics(record, str(record_path.relative_to(root)), errors)


def _validate_practical_templates(root: Path, errors: List[str]) -> None:
    template_root = root / "templates" / "practical"
    found = {path.name for path in template_root.glob("*.md")} if template_root.is_dir() else set()
    missing = REQUIRED_PRACTICAL_TEMPLATES - found
    if missing:
        errors.append(f"practical templates: missing {sorted(missing)}")
    for name in REQUIRED_PRACTICAL_TEMPLATES & found:
        path = template_root / name
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"practical templates: empty {name}")


def _validate_model_profiles_and_scenarios(
    root: Path, schema_by_version: Dict[str, Dict[str, Any]], errors: List[str]
) -> None:
    model_schema = schema_by_version.get("ai-film-studio/ModelProfile/v1")
    scenario_schema = schema_by_version.get("ai-film-studio/ScenarioFixture/v1")
    profile_root = root / "model-profiles"
    index = load_json(profile_root / "index.json", errors)
    if not isinstance(index, dict):
        return
    if index.get("default_delegation") != "seedance-2.5-v1.json":
        errors.append("model profile index: Seedance 2.5 must be the default delegation")
    profiles = index.get("profiles")
    if not isinstance(profiles, list):
        errors.append("model profile index: profiles must be a list")
        return
    expected_selection = {
        "seedance-2.5": "default-delegation",
        "kling": "explicit-only",
        "veo": "explicit-only",
        "future-model-template": "template-only",
    }
    observed_selection = {item.get("model_id"): item.get("selection") for item in profiles if isinstance(item, dict)}
    if observed_selection != expected_selection:
        errors.append("model profile index: required profile selections mismatch")
    for item in profiles:
        if not isinstance(item, dict):
            errors.append("model profile index: profile entry must be an object")
            continue
        raw_path = item.get("path")
        if not isinstance(raw_path, str) or not _relative_path_is_safe(raw_path):
            errors.append(f"model profile index: unsafe path for {item.get('model_id')}")
            continue
        profile_path = root / raw_path
        profile = load_json(profile_path, errors)
        if isinstance(profile, dict) and isinstance(model_schema, dict):
            validate_value(profile, model_schema, str(profile_path.relative_to(root)), errors)
            if profile.get("model_id") != item.get("model_id"):
                errors.append(f"{profile_path.relative_to(root)}: model_id mismatch with index")
            if profile.get("selection_policy") != item.get("selection"):
                errors.append(f"{profile_path.relative_to(root)}: selection mismatch with index")
    for profile_name in ("seedance-2.5-v1.json", "kling-v1.json", "veo-v1.json"):
        profile = load_json(profile_root / profile_name, errors)
        if not isinstance(profile, dict):
            continue
        expected_owner = "optional:video-production-studio:video-prompt-builder"
        if profile.get("prompt_formatter") != expected_owner or profile.get("validator") != expected_owner:
            errors.append(f"{profile_name}: optional format owner mismatch")
        if "local normalized packet contract" not in profile.get("first_party_evidence", []):
            errors.append(f"{profile_name}: local packet evidence is missing")

    e2e_root = root / "fixtures" / "end-to-end"
    found_e2e = {path.name for path in e2e_root.glob("*.json")} if e2e_root.is_dir() else set()
    missing_e2e = REQUIRED_END_TO_END_FIXTURES - found_e2e
    if missing_e2e:
        errors.append(f"end-to-end fixtures: missing {sorted(missing_e2e)}")
    for directory in (e2e_root, root / "fixtures" / "failure"):
        if not directory.is_dir():
            errors.append(f"scenario fixtures: missing {directory.relative_to(root)}")
            continue
        for fixture_path in sorted(directory.glob("*.json")):
            fixture = load_json(fixture_path, errors)
            if isinstance(fixture, dict) and isinstance(scenario_schema, dict):
                validate_value(fixture, scenario_schema, str(fixture_path.relative_to(root)), errors)
    failure_count = len(list((root / "fixtures" / "failure").glob("*.json"))) if (root / "fixtures" / "failure").is_dir() else 0
    if failure_count < 3:
        errors.append("failure fixtures: at least three are required")


def _validate_source_limits(root: Path, errors: List[str]) -> None:
    for directory in (root / "skills", root / "references"):
        for path in directory.rglob("*.md"):
            try:
                content = path.read_text(encoding="utf-8").upper()
            except OSError as error:
                errors.append(f"{path}: cannot scan source limits: {error}")
                continue
            for marker in SOURCE_MARKERS_TO_EXCLUDE:
                if marker in content:
                    errors.append(f"{path.relative_to(root)}: contains excluded captured-source marker {marker!r}")


def _validate_protocol(root: Path, errors: List[str]) -> None:
    try:
        advisor = _load_film_advisor(root)
    except Exception as error:
        errors.append(f"film_advisor.py: cannot load: {error}")
        return

    valid_packet = load_json(root / "fixtures" / "valid" / "film-advisor-packet.json", errors)
    external_packet = load_json(root / "fixtures" / "invalid" / "film-advisor-external-unapproved.json", errors)
    implicit_packet = load_json(root / "fixtures" / "invalid" / "film-advisor-implicit.json", errors)
    if isinstance(valid_packet, dict):
        result = advisor.evaluate_packet(valid_packet)
        if result.get("status") != "accepted" or result.get("skill") != "shot-continuity-director":
            errors.append("film_advisor.py: explicit planning fixture must route to shot-continuity-director")
    if isinstance(external_packet, dict):
        result = advisor.evaluate_packet(external_packet)
        if result.get("status") != "stopped" or result.get("reason") != "external_action_requires_approval":
            errors.append("film_advisor.py: unapproved external action must stop")
    if isinstance(implicit_packet, dict):
        result = advisor.evaluate_packet(implicit_packet)
        if result.get("status") != "stopped" or result.get("reason") != "activation_not_explicit":
            errors.append("film_advisor.py: implicit activation fixture must stop")

    topology = load_json(root / "references" / "film-advisor-topology.json", errors)
    if isinstance(topology, dict):
        expected = {
            "planner": ("planner", "gpt-5.6-sol", "high", False),
            "builder": ("builder", "gpt-5.6-terra", "max", True),
            "auditor": ("auditor", "gpt-5.6-sol", "xhigh", True),
            "fixer": ("fixer", "gpt-5.6-sol", "xhigh", True),
            "verifier": ("verifier", "gpt-5.6-sol", "xhigh", True),
        }
        for name, values in expected.items():
            role = topology.get(name, {})
            observed = (role.get("role"), role.get("model"), role.get("effort"), role.get("fresh_task"))
            if observed != values:
                errors.append(f"film-advisor-topology.json: invalid {name} mapping")
        independence = topology.get("independence", {})
        if independence != {"auditor_fixer_verifier_distinct": True, "overlapping_writes_serialized": True, "failed_verification_returns_to_planner": True, "uncontrolled_repair_loop": False}:
            errors.append("film-advisor-topology.json: independence policy mismatch")
        fallback = topology.get("fallback", {})
        if not isinstance(fallback, dict) or fallback.get("mode") != "local-bounded-planner":
            errors.append("film-advisor-topology.json: local bounded fallback is missing")
        if fallback.get("core_available_without_named_models") is not True:
            errors.append("film-advisor-topology.json: local core must remain available without named models")

        packet_names = ("AuditPacket", "FixPacket", "VerificationPacket")
        packets = [load_json(root / "templates" / f"{name}.json", errors) for name in packet_names]
        thread_ids = [packet.get("thread_id") for packet in packets if isinstance(packet, dict)]
        if len(thread_ids) != 3 or len(set(thread_ids)) != 3:
            errors.append("Film Advisor reviewer thread IDs must be present and distinct")


def _validate_public_boundary(root: Path, errors: List[str]) -> None:
    if (root / "IMPLEMENTATION-RECEIPT.json").exists():
        errors.append("IMPLEMENTATION-RECEIPT.json must not ship in the public package")
    prohibited = ("/" + "Users" + "/", "Israel " + "Ayliffe", "personal-plugins-" + "private")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".py", ".yaml", ".yml"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in prohibited:
            if marker in content:
                errors.append(f"{path.relative_to(root)}: contains prohibited public marker {marker!r}")
    source_attribution = root / "references" / "source-attribution.md"
    if source_attribution.is_file():
        digest = hashlib.sha256(source_attribution.read_bytes()).hexdigest()
        if digest != "a9d32c4a3863e64e8b0bc56b2fa2750e74636d588cc2e01e5864eb5717d60466":
            errors.append("references/source-attribution.md: protected source attribution changed")


def validate_bundle(root: Path) -> List[str]:
    root = root.resolve()
    errors: List[str] = []
    if not root.is_dir():
        return [f"bundle root does not exist: {root}"]
    manifest = load_json(root / ".codex-plugin" / "plugin.json", errors)
    if isinstance(manifest, dict):
        _validate_codex_manifest(root, manifest, errors)
        _validate_claude_manifest(root, manifest, errors)
    contract = load_json(root / "references" / "plugin-contract.json", errors)
    if isinstance(contract, dict):
        _validate_plugin_contract(root, contract, errors)
    schema_by_version = _validate_json_records(root, errors)
    _validate_stable_interfaces(root, schema_by_version, errors)
    _validate_practical_templates(root, errors)
    _validate_model_profiles_and_scenarios(root, schema_by_version, errors)
    _validate_source_limits(root, errors)
    _validate_protocol(root, errors)
    _validate_public_boundary(root, errors)
    return errors


def main(argv: Iterable[str]) -> int:
    args = list(argv)
    if len(args) != 2:
        print("usage: validate_bundle.py PLUGIN_ROOT", file=sys.stderr)
        return 2
    errors = validate_bundle(Path(args[1]))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("AI Film Studio bundle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
