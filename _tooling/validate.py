import json, os, pathlib, re, sys

# This repository (panopticon-diagrams) only contains diagrams; the source it is
# validated against lives in the three sibling repositories. By default we look for
# them as siblings of this repo's own checkout -- the layout you get by cloning all
# four Panopticon-Co repos into one parent directory. Override with the
# PANOPTICON_WORKSPACE environment variable if your layout differs.
DIAG = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = pathlib.Path(os.environ.get("PANOPTICON_WORKSPACE", DIAG.parent))
AGENT = WORKSPACE / "panopticon-agent"
ENGINE = WORKSPACE / "panopticon-detection-engine"
CONSOLE = WORKSPACE / "panopticon-console"
MANAGER = WORKSPACE / "panopticon-manager"
LINUX_AGENT = WORKSPACE / "panopticon-linux-agent"
SKIP = (".git", ".venv", "build-officer-x64", "build", "__pycache__", ".pytest_cache", "vendor")

missing = [str(p) for p in (AGENT, MANAGER, ENGINE, CONSOLE, LINUX_AGENT) if not p.is_dir()]
if missing:
    print("validate.py needs the five source repositories checked out beside this one:")
    for p in missing:
        print("  missing:", p)
    print()
    print("Clone panopticon-agent, panopticon-manager, panopticon-detection-engine,")
    print("panopticon-console and panopticon-linux-agent as siblings of this repository,")
    print("or set PANOPTICON_WORKSPACE to the directory that contains all five.")
    sys.exit(2)

def read_all(base, pats):
    out = []
    for pat in pats:
        for f in base.rglob(pat):
            if any(s in f.parts for s in SKIP):
                continue
            out.append(f.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(out)

agent_src = read_all(AGENT, ("*.hpp", "*.cpp", "CMakeLists.txt"))
engine_src = read_all(ENGINE, ("*.py",))
console_src = read_all(CONSOLE, ("*.py", "*.js"))
manager_src = read_all(MANAGER, ("*.py",))
linux_agent_src = read_all(LINUX_AGENT, ("*.hpp", "*.cpp", "CMakeLists.txt"))
all_src = agent_src + manager_src + engine_src + console_src + linux_agent_src
schema = json.loads((AGENT / "schema" / "event.schema.json").read_text(encoding="utf-8"))
fails = []
checks = [0]

def check(label, ok, detail=""):
    checks[0] += 1
    if not ok:
        fails.append(label + "  " + detail)

IDENTIFIERS = [
 "TelemetryCollector","EtwProcessCollector","SysmonEventCollector","SysmonProcessDecoder",
 "SysmonTelemetryDecoder","RawProcessEvent","EnrichedProcessEvent","PanopticonEvent",
 "ProcessMetadata","ParentProcessMetadata","ProcessHashMetadata","SourceProvenance",
 "RawEventSink","normalize_process_event","serialize_event","derive_process_entity_id",
 "derive_process_event_id","derive_process_context_entity_id","officer-core",
 "officer-collectors","officer-agent","officer-query",
 "DetectionRun","RuleEvaluator","ConditionMatcher","DetectionResult","Alert","LogicNode",
 "Condition","Rule","ProcessTree","ThreatIntelEngine","ThresholdEngine","CorrelationEngine",
 "EntityRiskScorer","C2BeaconDetector","PortScanDetector","RansomwareShield",
 "IdentityAnalyticsEngine","CloudThreatEngine","EnterpriseAttackGraph",
 "EndpointRemediationEngine","RemediationAction","ActiveResponseEngine","ActiveResponseAction",
 "BoundedEventQueue","StreamingPipeline","AlertSpool","IncrementalAlertWriter","RetryPolicy",
 "HealthState","Metrics","OfficerIngestionAdapter","LiveTelemetryStream",
 "process_event","evaluate_event","set_rules","from_detection_result","to_dict",
 "claim_deliverable","mark_delivered","mark_failed","requeue_dead","already_delivered",
 "transform_officer_event","stream_from_officer_process","stream_from_file",
 "_rules_by_type","_matched_rules_history","_evaluate_logic_node","_extract_evidence",
 "matched_evidence","active_response","auto_remediate","action_history","nodes_by_guid",
 "active_pids","get_ancestors","has_ancestor","next_attempt_at","alert_id","threat_intel",
 "process_tree","threshold_engine","correlation_engine","remediate_threat","resolve_action",
]
for ident in IDENTIFIERS:
    check("MISSING IDENTIFIER", ident in all_src, ident)

props = schema["properties"]
for block in ("schema_version","event","source","agent","host","user","process","network","file","registry","image_load"):
    check("MISSING SCHEMA BLOCK", block in props, block)
for f in ("id","category","type","timestamp"):
    check("MISSING event field", f in props["event"]["properties"], f)
for f in ("kind","provider","channel","record_id"):
    check("MISSING source field", f in props["source"]["properties"], f)
for f in ("entity_id","pid","name","executable","command_line","parent","hash"):
    check("MISSING process field", f in props["process"]["properties"], f)
for f in ("direction","protocol","source_ip","source_port","destination_ip","destination_port","destination_hostname"):
    check("MISSING network field", f in props["network"]["properties"], f)
for f in ("operation","path","target_path","previous_path","hash"):
    check("MISSING file field", f in props["file"]["properties"], f)
for f in ("operation","key_path","value_name","value_type","value_data"):
    check("MISSING registry field", f in props["registry"]["properties"], f)
for f in ("path","is_signed","signature_status","hash"):
    check("MISSING image_load field", f in props["image_load"]["properties"], f)

check("SCHEMA VERSIONS", set(props["schema_version"]["enum"]) == {"0.2","0.3","0.4"}, str(props["schema_version"]["enum"]))
check("CATEGORY ENUM", set(props["event"]["properties"]["category"]["enum"]) == {"process","network","file","registry","image_load"}, "")
check("STRICT SCHEMA", schema.get("additionalProperties") is False, "")
check("PROCESS ALWAYS REQUIRED", "process" in schema["required"], "")

n_rules = len(list((ENGINE / "rules").rglob("*.yaml")))
check("RULE COUNT", n_rules == 92, "found " + str(n_rules) + ", diagrams say 92")
n_domains = len([d for d in (ENGINE / "rules").iterdir() if d.is_dir()])
check("RULE DOMAIN COUNT", n_domains == 16, "found " + str(n_domains) + ", spec says 16")
ops = re.search(r"OPERATOR_MAP\s*=\s*\{(.*?)\}", engine_src, re.S)
n_ops = len(re.findall(r'"\w+":', ops.group(1))) if ops else 0
check("OPERATOR COUNT", n_ops == 13, "found " + str(n_ops) + ", diagrams say 13")
check("SCHEMA VERSION CONST", 'kSchemaVersion[] = "0.3"' in agent_src, "")
check("AGENT VERSION CONST", 'kAgentVersion[] = "0.3.0"' in agent_src, "")
check("ENGINE ACCEPTS 0.1-0.3", '("0.1", "0.2", "0.3")' in engine_src, "")
check("QUEUE DEFAULT 1024", "default=1024" in engine_src, "")
check("CONSOLE POLL 3000MS", "POLL_INTERVAL_MS = 3000" in console_src, "")
check("CONSOLE PORT 8787", "8787" in console_src, "")
for s in ("PENDING","DELIVERED","DEAD"):
    check("SPOOL STATE", 'STATUS_' + s + ' = "' + s.lower() + '"' in engine_src, s)

rem_files = [f for f in (ENGINE / "src" / "remediation").rglob("*.py") if "__pycache__" not in f.parts]
rem_src = "\n".join(f.read_text(encoding="utf-8") for f in rem_files)
for danger in ("subprocess", "os.kill", "winreg", "socket.", "os.remove", "shutil.move"):
    check("REMEDIATION EXECUTES", danger not in rem_src, danger + " found in src/remediation")

check("CONSOLE READ-ONLY", "do_POST" not in console_src and "do_PUT" not in console_src, "")
check("MANAGER INGEST ROUTE", '@router.post("/api/v1/ingest"' in manager_src, "")
check("MANAGER EVENT DEDUP", "INSERT OR IGNORE INTO events" in manager_src, "")
check("MANAGER DETECTION WORKER", "class DetectionWorker" in manager_src, "")
check("MANAGER CLAIM LOOP", "detect_state='claimed'" in manager_src, "")
command_route_files = [f for f in (MANAGER / "manager" / "routers").glob("commands.py")]
command_route_src = "\n".join(f.read_text(encoding="utf-8") for f in command_route_files)
check("COMMAND ROUTE FILE FOUND", bool(command_route_src), "manager/routers/commands.py")
check("COMMAND ENDPOINT AUTH REQUIRED", "PANOPTICON_COMMAND_TOKEN" in command_route_src and "hmac.compare_digest" in command_route_src, "")
CLOSED_ACTION_SET = {
    "KILL_PROCESS", "COLLECT_PROCESS_INFO", "COLLECT_NETWORK_CONNECTIONS",
    "COLLECT_FILE", "QUARANTINE_FILE", "ISOLATE_HOST", "RELEASE_HOST_ISOLATION",
}
# The closed action Literal and the tier table below both moved out of
# manager/ and into the extracted panopticon-response-engine domain package
# (vendored into Manager as vendor/response_engine), which read_all()
# deliberately excludes from manager_src via SKIP -- read it directly here
# instead of assuming it still lives inline in Manager's own source.
response_engine_pkg = MANAGER / "vendor" / "response_engine" / "response_engine"
def read_vendored(name):
    p = response_engine_pkg / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""
response_engine_contract_src = read_vendored("contract.py")
response_engine_policy_src = read_vendored("policy.py")
check("RESPONSE ENGINE VENDORED CONTRACT FOUND", bool(response_engine_contract_src),
      "vendor/response_engine/response_engine/contract.py")
action_literal = re.search(r"Action = Literal\[(.*?)\]", response_engine_contract_src, re.S)
manager_actions = set(re.findall(r'"([A-Z_]+)"', action_literal.group(1))) if action_literal else set()
check("COMMAND ACTION SET CLOSED (exactly 7, manager)", manager_actions == CLOSED_ACTION_SET,
      "found " + str(sorted(manager_actions)))
for danger in ("subprocess", "os.system", "popen(", "os.exec"):
    check("NO SHELL EXEC IN MANAGER COMMAND ROUTE", danger not in command_route_src, danger + " found in manager/routers/commands.py")

# The Linux agent's command parser is the other half of the closed action set
# -- both sides must agree exactly, or a 7th/8th action could exist on one
# side without the other rejecting it.
linux_command_files = [f for f in (LINUX_AGENT / "src").glob("command.cpp")]
linux_command_src = "\n".join(f.read_text(encoding="utf-8") for f in linux_command_files)
check("LINUX AGENT COMMAND FILE FOUND", bool(linux_command_src), "src/command.cpp")
linux_actions = set(re.findall(r'action == "([A-Z_]+)"', linux_command_src))
check("COMMAND ACTION SET CLOSED (exactly 7, linux agent)", linux_actions == CLOSED_ACTION_SET,
      "found " + str(sorted(linux_actions)))

# Host isolation: exactly 2 opcodes, no free-form content, no shell/exec
# anywhere in the privileged helper (ADR 004 -- see docs/adr in
# panopticon-linux-agent). This is the one process in the whole system that
# holds CAP_NET_ADMIN, so this check matters more than most.
isolation_hpp_files = [f for f in (LINUX_AGENT / "include").rglob("isolation.hpp")]
isolation_hpp_src = "\n".join(f.read_text(encoding="utf-8") for f in isolation_hpp_files)
check("ISOLATION HPP FOUND", bool(isolation_hpp_src), "include/panopticon/linux_agent/isolation.hpp")
opcodes = set(re.findall(r"(\w+)\s*=\s*\d+U?,", re.search(r"enum class isolation_opcode.*?\{(.*?)\}", isolation_hpp_src, re.S).group(1))) if "enum class isolation_opcode" in isolation_hpp_src else set()
check("ISOLATION IPC EXACTLY 2 OPCODES", opcodes == {"isolate", "release"}, "found " + str(sorted(opcodes)))
isolation_impl_files = [
    f for f in (LINUX_AGENT / "src").glob("isolation*.cpp")
]
isolation_impl_src = "\n".join(f.read_text(encoding="utf-8") for f in isolation_impl_files)
check("ISOLATION IMPL FOUND", bool(isolation_impl_src), "src/isolation*.cpp")
for danger in ("system(", "popen(", "execve(", "execvp(", "execl(", "execlp(", "/bin/sh"):
    check("NO SHELL EXEC IN ISOLATION HELPER", danger not in isolation_impl_src, danger + " found in linux-agent isolation source")

# Response Engine tier defaults -- KILL_PROCESS/ISOLATE_HOST/RELEASE_HOST_ISOLATION
# must always require analyst approval; the two read-only collectors are the
# only actions ever allowed to auto-enqueue. A regression here would let a
# detection auto-fire a destructive action, silently violating a locked
# design decision.
check("RESPONSE ENGINE VENDORED POLICY FOUND", bool(response_engine_policy_src),
      "vendor/response_engine/response_engine/policy.py")
tiers_block = re.search(r"_TIERS[^=]*=\s*\{(.*?)\}", response_engine_policy_src, re.S)
# Values are Tier.AUTO_SAFE / Tier.ANALYST_APPROVAL enum members, not quoted
# strings, since this table moved from a plain manager-local dict into the
# extracted response_engine.policy module's typed Tier enum.
tiers = dict(re.findall(r'"([A-Z_]+)":\s*Tier\.([A-Z_]+)', tiers_block.group(1))) if tiers_block else {}
for always_approval in ("KILL_PROCESS", "ISOLATE_HOST", "RELEASE_HOST_ISOLATION"):
    check("RESPONSE TIER ALWAYS ANALYST_APPROVAL", tiers.get(always_approval) == "ANALYST_APPROVAL", always_approval + " -> " + str(tiers.get(always_approval)))
for auto_safe in ("COLLECT_PROCESS_INFO", "COLLECT_NETWORK_CONNECTIONS"):
    check("RESPONSE TIER AUTO_SAFE FOR READ-ONLY ACTIONS", tiers.get(auto_safe) == "AUTO_SAFE", auto_safe + " -> " + str(tiers.get(auto_safe)))
check("MANAGER RESPONSE ACTIONS ROUTES", all(
    route in manager_src for route in (
        '@router.get("/api/v1/response-actions"',
        '@router.post("/api/v1/response-actions/{response_id}/authorize"',
        '@router.post("/api/v1/response-actions/{response_id}/reject"',
    )
), "")
check("MANAGER ALERTS QUERY ROUTE", '@router.get("/api/v1/alerts"' in manager_src, "")

# Console's response-actions view stays a same-origin, read-only proxy: no
# cross-origin fetch, no mutating route, per the locked "console never
# executes a response" boundary.
check("CONSOLE RESPONSE ACTIONS PROXY ROUTE", '"/api/response-actions"' in console_src, "")
check("CONSOLE NEVER CALLS MANAGER FROM THE BROWSER", "/api/v1/response-actions" not in read_all(CONSOLE, ("*.js",)), "")

for f in sorted(DIAG.rglob("*.html")):
    t = f.read_text(encoding="utf-8")
    check("NO role=img", 'role="img"' in t, f.name)
    check("NO aria-labelledby", "aria-labelledby" in t, f.name)
    check("MULTIPLE viewBox", t.count("viewBox=") == 1, f.name)
    check("HAS SCRIPT", "<script" not in t, f.name)

BANNED = ["named pipe", "Named Pipe", "84+", "REST API", "Kafka"]
for f in sorted(DIAG.rglob("*.html")):
    t = f.read_text(encoding="utf-8")
    for b in BANNED:
        check("BANNED TERM", b not in t, repr(b) + " in " + f.name)

print(str(checks[0]) + " checks run")
if fails:
    print("")
    print(str(len(fails)) + " FAILURES:")
    for x in fails:
        print("  - " + x)
    sys.exit(1)
print("ALL CONSISTENCY CHECKS PASSED")
