import os
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

def test_operator_bundle():
    print("=" * 70)
    print("🔴 RED HAT ECOSYSTEM CATALOG & OPERATOR CERTIFICATION VERIFIER")
    print("=" * 70)
    
    # 1. Check Directory Structure
    print("\n[1/5] Verifying Operator Bundle Directory Layout...")
    manifests_dir = BUNDLE_DIR / "manifests"
    metadata_dir = BUNDLE_DIR / "metadata"
    
    assert manifests_dir.exists(), "Missing bundle/manifests directory"
    assert metadata_dir.exists(), "Missing bundle/metadata directory"
    print("   ✓ Bundle directory structure verified.")

    # 2. Verify Annotations
    print("\n[2/5] Validating metadata/annotations.yaml...")
    annotations_file = metadata_dir / "annotations.yaml"
    assert annotations_file.exists(), "Missing annotations.yaml"
    
    with open(annotations_file, "r", encoding="utf-8") as f:
        annot_data = yaml.safe_load(f)
    
    annotations = annot_data.get("annotations", {})
    required_annotations = [
        "operators.operatorframework.io.bundle.mediatype.v1",
        "operators.operatorframework.io.bundle.manifests.v1",
        "operators.operatorframework.io.bundle.metadata.v1",
        "operators.operatorframework.io.bundle.package.v1",
        "operators.operatorframework.io.bundle.channels.v1",
        "operators.operatorframework.io.bundle.channel.default.v1"
    ]
    for r in required_annotations:
        assert r in annotations, f"Missing required annotation: {r}"
        print(f"   ✓ {r} = {annotations[r]}")

    # 3. Validate ClusterServiceVersion (CSV)
    print("\n[3/5] Validating ClusterServiceVersion (CSV)...")
    csv_file = manifests_dir / "bob-edge-operator.clusterserviceversion.yaml"
    assert csv_file.exists(), "Missing CSV manifest file"
    
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_data = yaml.safe_load(f)
        
    spec = csv_data.get("spec", {})
    assert spec.get("displayName"), "CSV missing displayName"
    assert spec.get("version"), "CSV missing version"
    assert spec.get("installModes"), "CSV missing installModes"
    assert spec.get("customresourcedefinitions", {}).get("owned"), "CSV missing owned CRDs"
    
    print(f"   ✓ Display Name: {spec.get('displayName')}")
    print(f"   ✓ Operator Version: {spec.get('version')}")
    print(f"   ✓ Capabilities: {csv_data.get('metadata', {}).get('annotations', {}).get('capabilities')}")

    # 4. Validate CRD Match
    print("\n[4/5] Validating CustomResourceDefinition (CRD) Alignment...")
    crd_file = manifests_dir / "automation.bob-edge.io_bobedgedeployments.yaml"
    assert crd_file.exists(), "Missing CRD file"
    with open(crd_file, "r", encoding="utf-8") as f:
        crd_data = yaml.safe_load(f)
    
    crd_name = crd_data.get("metadata", {}).get("name")
    owned_crds = [c.get("name") for c in spec.get("customresourcedefinitions", {}).get("owned", [])]
    assert crd_name in owned_crds, f"CRD {crd_name} not declared in CSV owned list"
    print(f"   ✓ CRD {crd_name} correctly aligned with CSV declaration.")

    # 5. Red Hat Preflight Standards Emulation
    print("\n[5/5] Emulating Red Hat OpenShift Preflight Security Checks...")
    deployments = spec.get("install", {}).get("spec", {}).get("deployments", [])
    assert len(deployments) > 0, "No deployments specified in CSV"
    
    for dep in deployments:
        containers = dep.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        for c in containers:
            sec_ctx = c.get("securityContext", {})
            assert sec_ctx.get("allowPrivilegeEscalation") is False, "allowPrivilegeEscalation must be False"
            assert sec_ctx.get("runAsNonRoot") is True, "runAsNonRoot must be True"
            print(f"   ✓ Container '{c.get('name')}': Non-root execution & privilege escalation blocked.")

    print("\n" + "=" * 70)
    print("🎉 ALL RED HAT OPERATOR ECOSYSTEM BUNDLE CHECKS PASSED!")
    print("=" * 70 + "\n")
    return True

if __name__ == "__main__":
    test_operator_bundle()
