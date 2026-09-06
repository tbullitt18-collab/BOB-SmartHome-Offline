#!/usr/bin/env python3
"""
Red Hat Preflight Static Policy & SecurityContext Constraints Verifier
Validates OpenShift certified operator compliance:
- restricted-v2 SecurityContextConstraints (SCC)
- Non-root UID execution
- Blocked privilege escalation
- Red Hat delivery & version annotations
"""

import sys
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent
BUNDLE_DIR = ROOT_DIR / "commercial" / "ieam-openshift" / "openshift" / "operator" / "bundle"

def verify_preflight():
    print("=" * 70)
    print("🛡️ RED HAT PREFLIGHT STATIC POLICY & SCC SECURITY AUDIT")
    print("=" * 70)

    # 1. Annotations Audit
    print("\n[1/3] Auditing metadata/annotations.yaml...")
    annot_file = BUNDLE_DIR / "metadata" / "annotations.yaml"
    assert annot_file.exists(), f"Annotations file missing: {annot_file}"

    with open(annot_file, "r", encoding="utf-8") as f:
        annot_data = yaml.safe_load(f).get("annotations", {})

    assert annot_data.get("com.redhat.openshift.versions") == "v4.12-v4.17", \
        f"Invalid OpenShift version range: {annot_data.get('com.redhat.openshift.versions')}"
    assert annot_data.get("com.redhat.delivery.operator.bundle") == "true", \
        f"Missing or invalid bundle delivery flag: {annot_data.get('com.redhat.delivery.operator.bundle')}"
    print("   [OK] Target OpenShift versions: v4.12-v4.17")
    print("   [OK] Bundle delivery flag confirmed.")

    # 2. ClusterServiceVersion SecurityContextConstraints Audit
    print("\n[2/3] Auditing CSV SecurityContextConstraints (SCC restricted-v2)...")
    csv_file = BUNDLE_DIR / "manifests" / "bob-edge-operator.clusterserviceversion.yaml"
    assert csv_file.exists(), f"CSV file missing: {csv_file}"

    with open(csv_file, "r", encoding="utf-8") as f:
        csv_data = yaml.safe_load(f)

    deployments = csv_data.get("spec", {}).get("install", {}).get("spec", {}).get("deployments", [])
    assert len(deployments) > 0, "No deployments defined in CSV install spec"

    checked_containers = 0
    for dep in deployments:
        dep_name = dep.get("name", "unnamed-deployment")
        template_spec = dep.get("spec", {}).get("template", {}).get("spec", {})
        containers = template_spec.get("containers", [])
        assert len(containers) > 0, f"No containers found in deployment {dep_name}"

        for c in containers:
            c_name = c.get("name")
            sec_ctx = c.get("securityContext", {})
            assert sec_ctx.get("allowPrivilegeEscalation") is False, \
                f"Container '{c_name}' must have allowPrivilegeEscalation: false"
            assert sec_ctx.get("runAsNonRoot") is True, \
                f"Container '{c_name}' must have runAsNonRoot: true"
            print(f"   [OK] Deployment '{dep_name}' / Container '{c_name}': allowPrivilegeEscalation=False, runAsNonRoot=True")
            checked_containers += 1

    assert checked_containers > 0, "No containers were verified"

    # 3. CRD OpenAPI Schema Audit
    print("\n[3/3] Auditing CustomResourceDefinition Schema...")
    crd_file = BUNDLE_DIR / "manifests" / "automation.bob-edge.io_bobedgedeployments.yaml"
    assert crd_file.exists(), f"CRD file missing: {crd_file}"
    with open(crd_file, "r", encoding="utf-8") as f:
        crd_data = yaml.safe_load(f)

    crd_spec = crd_data.get("spec", {})
    versions = crd_spec.get("versions", [])
    assert len(versions) > 0, "No versions found in CRD"
    for v in versions:
        assert v.get("schema", {}).get("openAPIV3Schema"), f"CRD version {v.get('name')} missing openAPIV3Schema"
        print(f"   [OK] CRD version '{v.get('name')}' contains valid openAPIV3Schema.")

    print("\n" + "=" * 70)
    print("✅ PREFLIGHT STATIC POLICY & SCC CHECKS FULLY PASSED!")
    print("=" * 70 + "\n")
    return True

if __name__ == "__main__":
    verify_preflight()
