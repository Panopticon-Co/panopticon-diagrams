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
SKIP = (".git", ".venv", "build-officer-x64", "__pycache__", ".pytest_cache")

missing = [str(p) for p in (AGENT, ENGINE, CONSOLE) if not p.is_dir()]
if missing:
    print("validate.py needs the three source repositories checked out beside this one:")
    for p in missing:
        print("  missing:", p)
    print()
    print("Clone panopticon-agent, panopticon-detection-engine and panopticon-console")
    print("as siblings of this repository, or set PANOPTICON_WORKSPACE to the directory")
    print("that contains all three.")
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
all_src = agent_src + engine_src + console_src
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

check("SCHEMA VERSIONS", set(props["schema_version"]["enum"]) == {"0.2","0.3"}, str(props["schema_version"]["enum"]))
check("CATEGORY ENUM", set(props["event"]["properties"]["category"]["enum"]) == {"process","network","file","registry","image_load"}, "")
check("STRICT SCHEMA", schema.get("additionalProperties") is False, "")
check("PROCESS ALWAYS REQUIRED", "process" in schema["required"], "")

n_rules = len(list((ENGINE / "rules").rglob("*.yaml")))
check("RULE COUNT", n_rules == 86, "found " + str(n_rules) + ", diagrams say 86")
n_domains = len([d for d in (ENGINE / "rules").iterdir() if d.is_dir()])
check("RULE DOMAIN COUNT", n_domains == 15, "found " + str(n_domains) + ", spec says 15")
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
