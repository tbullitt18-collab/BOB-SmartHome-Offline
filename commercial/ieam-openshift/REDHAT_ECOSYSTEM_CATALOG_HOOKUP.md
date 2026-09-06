# Red Hat Ecosystem Catalog & OperatorHub Publishing Runbook

**Solution:** BOB Edge Automation & Disaster Resilience Platform  
**Operator Package:** `bob-edge-operator`  
**Target Catalogs:** Red Hat Ecosystem Catalog, Red Hat OpenShift OperatorHub, OperatorHub.io  
**Supported OpenShift Versions:** `v4.12` through `v4.17`  
**Maintained By:** BOB Edge Systems (support@bob-edge.io)  

---

## 1. Executive & Architectural Overview

The **Red Hat Ecosystem Catalog** and **OpenShift OperatorHub** provide enterprise customers, utilities, and telecommunications operators with one-click, certified deployment of BOB on OpenShift clusters and Red Hat Device Edge (MicroShift) nodes.

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             RED HAT ECOSYSTEM PIPELINE                           │
└──────────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ 1. Local Bundle Build   │ ───► │ 2. Quay.io & Preflight  │ ───► │ 3. GitHub Cert PR       │
│ - Manifests (CSV, CRD)  │      │ - quay.io/bob-edge/...  │      │ - redhat-openshift-     │
│ - Metadata annotations  │      │ - preflight check       │      │   ecosystem/certified-  │
│ - bundle.Dockerfile     │      │ - Partner Connect Token │      │   operators             │
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                               │
                                                                               ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. Published in Red Hat Ecosystem Catalog & OpenShift In-Cluster OperatorHub              │
│    Customers install via OLM: `Subscription` -> `bob-edge-operator` (Channel: stable)     │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Red Hat Partner Connect Portal Setup

### Step 2.1: Access Partner Connect & Enrollment Status
1. **Enrollment Status:** **SUBMITTED & IN REVIEW** (RHPP Build Module / ISV Track).
   * **Applicant:** Todd Bullitt (`tbullitt18@gmail.com`)
   * **Company Entity:** `BOB Edge Systems`
   * **Program Track:** Red Hat Partner Program - **Build Module** (Validation & Certification of Software / Operators on OpenShift & RHEL)
   * **Submission Confirmation:** Form submitted via Red Hat CRM Partner Onboarding portal. Application pending vetting review.
2. Portal Dashboard: [connect.redhat.com](https://connect.redhat.com).

### Step 2.2: Create Operator Certification Project
1. In the Partner Connect dashboard, click **Certification Zones** > **Container & Operator Projects**.
2. Click **Create Project** > **OpenShift Operator**.
3. Fill in the certification project profile:
   * **Project Name:** `BOB Edge Automation Platform`
   * **Product Name:** `BOB: Offline Smart Home Survival System & Physical DevOps Platform`
   * **Operator Package Name:** `bob-edge-operator`
   * **Repository Host:** `Quay.io`
   * **Distribution:** `Red Hat OpenShift Container Platform`
   * **Target Versions:** `4.12, 4.13, 4.14, 4.15, 4.16, 4.17`
   * **Support Contact:** `support@bob-edge.io`
4. Click **Create Project**.

### Step 2.3: Retrieve Preflight API Certification Token
1. In your newly created project dashboard, navigate to the **Preflight** or **Settings** tab.
2. Under **Certification Key / Preflight Token**, click **Generate Token**.
3. Save this value securely. Export it in your local environment and GitHub Secrets:
   ```bash
   export PFLT_CERTIFICATION_TOKEN="<YOUR_RED_HAT_PREFLIGHT_TOKEN>"
   ```

---

## 3. Container Images & Quay.io Registry Setup

Red Hat certification requires operator controller images and bundle images to reside in a publicly accessible or robot-authenticated registry (Quay.io is strongly recommended and natively integrated).

### Step 3.1: Create Quay.io Repositories
Create two repositories on [quay.io](https://quay.io) under the `bob-edge` organization:
1. `quay.io/bob-edge/operator` (Container controller runtime)
2. `quay.io/bob-edge/operator-bundle` (Operator bundle image)

### Step 3.2: Build and Push the Operator Controller Image
```bash
# Build the controller image
docker build -t quay.io/bob-edge/operator:v1.0.0 -f Dockerfile .

# Push to Quay.io
docker push quay.io/bob-edge/operator:v1.0.0
```

### Step 3.3: Build and Push the Operator Bundle Image
The bundle files are located in `commercial/ieam-openshift/openshift/operator/bundle/`.

```bash
cd commercial/ieam-openshift/openshift/operator/bundle

# Build the OCI bundle image
docker build -t quay.io/bob-edge/operator-bundle:v1.0.0 -f - . <<EOF
FROM scratch
LABEL operators.operatorframework.io.bundle.mediatype.v1=registry+v1
LABEL operators.operatorframework.io.bundle.manifests.v1=manifests/
LABEL operators.operatorframework.io.bundle.metadata.v1=metadata/
LABEL operators.operatorframework.io.bundle.package.v1=bob-edge-operator
LABEL operators.operatorframework.io.bundle.channels.v1=stable,fast
LABEL operators.operatorframework.io.bundle.channel.default.v1=stable
LABEL com.redhat.openshift.versions="v4.12-v4.17"
LABEL com.redhat.delivery.operator.bundle="true"
COPY manifests /manifests/
COPY metadata /metadata/
EOF

# Push bundle image to Quay.io
docker push quay.io/bob-edge/operator-bundle:v1.0.0
```

---

## 4. Local Preflight & Bundle Verification

Before upstream submission, verify bundle compliance using the verification script and the official Red Hat Preflight CLI tool.

### Step 4.1: Run Internal Bundle Verifier
```bash
python scripts/verify_redhat_operator.py
```
Expected output:
```text
======================================================================
🔴 RED HAT ECOSYSTEM CATALOG & OPERATOR CERTIFICATION VERIFIER
======================================================================
[1/5] Verifying Operator Bundle Directory Layout... ✓
[2/5] Validating metadata/annotations.yaml... ✓
[3/5] Validating ClusterServiceVersion (CSV)... ✓
[4/5] Validating CustomResourceDefinition (CRD) Alignment... ✓
[5/5] Emulating Red Hat OpenShift Preflight Security Checks... ✓
======================================================================
🎉 ALL RED HAT OPERATOR ECOSYSTEM BUNDLE CHECKS PASSED!
======================================================================
```

### Step 4.2: Run Operator SDK Bundle Validator
```bash
operator-sdk bundle validate commercial/ieam-openshift/openshift/operator/bundle --select-optional name=operatorhub
```

### Step 4.3: Execute Red Hat Preflight Check
Download and run the official Red Hat Preflight CLI tool:
```bash
# Install preflight CLI
curl -sLO https://github.com/redhat-openshift-ecosystem/openshift-preflight/releases/latest/download/preflight-linux-amd64
chmod +x preflight-linux-amd64
sudo mv preflight-linux-amd64 /usr/local/bin/preflight

# Run preflight operator check and auto-submit results to Partner Connect
preflight check operator quay.io/bob-edge/operator-bundle:v1.0.0 \
  --certification-token="$PFLT_CERTIFICATION_TOKEN" \
  --submit
```

---

## 5. Upstream OperatorHub & Catalog Submission

Publishing to the Red Hat OpenShift OperatorHub and Red Hat Ecosystem Catalog is managed via pull request against the official GitHub repositories.

### Step 5.1: Fork the Certified Operators Repository
Fork [redhat-openshift-ecosystem/certified-operators](https://github.com/redhat-openshift-ecosystem/certified-operators) on GitHub.

```bash
git clone https://github.com/<YOUR_GITHUB_USER>/certified-operators.git
cd certified-operators
git checkout -b add-bob-edge-operator-v1.0.0
```

### Step 5.2: Populate Operator Package Structure
Create the operator package directory:
```bash
mkdir -p operators/bob-edge-operator/1.0.0
mkdir -p operators/bob-edge-operator/ci

# Copy bundle manifests
cp -r <BOB_REPO_ROOT>/commercial/ieam-openshift/openshift/operator/bundle/manifests/* \
  operators/bob-edge-operator/1.0.0/

# Copy bundle metadata
cp -r <BOB_REPO_ROOT>/commercial/ieam-openshift/openshift/operator/bundle/metadata \
  operators/bob-edge-operator/1.0.0/

# Create operators/bob-edge-operator/ci.yaml for CI automation
cat <<EOF > operators/bob-edge-operator/ci.yaml
---
reviewers:
  - tbullitt18-collab
updateGraph: replaces-mode
EOF
```

Directory tree structure in PR:
```text
operators/bob-edge-operator/
├── ci.yaml
└── 1.0.0
    ├── manifests
    │   ├── automation.bob-edge.io_bobedgedeployments.yaml
    │   └── bob-edge-operator.clusterserviceversion.yaml
    └── metadata
        └── annotations.yaml
```

### Step 5.3: Commit and Open Upstream Pull Request
```bash
git add operators/bob-edge-operator
git commit -m "feat(operator): add bob-edge-operator v1.0.0 certification bundle"
git push origin add-bob-edge-operator-v1.0.0
```

1. Open a Pull Request from your branch to `redhat-openshift-ecosystem/certified-operators:main`.
2. Title: `operator: bob-edge-operator (1.0.0)`
3. The Red Hat automated test bot (`openshift-ci-bot`) will automatically spin up an ephemeral OpenShift 4.12+ cluster, install the operator bundle, and verify:
   * Non-root execution
   * Resource limit compliance
   * CRD OpenAPI v3 schema validation
   * Clean install and upgrade lifecycle
4. Once tests turn green (`approved`, `lgtm`), Red Hat engineers merge the PR.

---

## 6. Verification: Installing in OpenShift Cluster

Once merged and published, enterprise users can install BOB directly from OpenShift CLI or Web Console.

### Via OpenShift Web Console:
1. Open the OpenShift Web Console.
2. Navigate to **Operators** > **OperatorHub**.
3. Search for `BOB Edge Automation`.
4. Click **Install**, choose channel `stable`, and set approval strategy to `Automatic`.

### Via OpenShift CLI Manifest:
```yaml
# bob-subscription.yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: bob-edge-operator-sub
  namespace: openshift-operators
spec:
  channel: stable
  name: bob-edge-operator
  source: certified-operators
  sourceNamespace: openshift-marketplace
```

```bash
oc apply -f bob-subscription.yaml
```

### Deploying the Resilient Microgrid Cluster CR:
```bash
oc apply -f commercial/ieam-openshift/openshift/operator/crd-bob-edge.yaml
```

---

## 7. Ongoing CI/CD Automation

This repository includes `.github/workflows/redhat-certification.yml`. Any change to operator manifests, annotations, or security contexts triggers automated preflight linting and bundle validation on every commit.
