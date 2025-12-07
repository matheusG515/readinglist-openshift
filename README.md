# OpenShift Capstone Project – Reading List Application

## Overview

This capstone project demonstrates my hands-on experience with **OpenShift 4 (Developer Sandbox)** and highlights multiple ways to build, deploy, configure, scale, and manage applications using platform-native tooling.

The project centers around a **single Python Flask application** backed by **PostgreSQL**, intentionally deployed using **two different deployment strategies** to showcase OpenShift’s flexibility:

1. A **raw Kubernetes/OpenShift deployment** managed via Tekton pipelines  
2. A **Helm-managed deployment** using a reusable chart and release model  

Both deployments run **simultaneously**, share the **same database**, and use the **same container image**, but are managed independently to highlight different operational models.

---

## Application Architecture

### Application
- **Reading List API**
- Python + Flask
- Stateless application
- Same container image used across all deployments

### Endpoints
- `/` – HTML frontend  
- `/books` – GET / POST book entries  
- `/healthz` – health check  
- `/config` – exposes runtime config (banner + environment)

### Database
- PostgreSQL
- Single instance
- Backed by a PersistentVolumeClaim
- Configured to run with OpenShift’s non-root security constraints
- Used by **both deployments** simultaneously

This shared-database design proves that the application is stateless and horizontally scalable, regardless of deployment mechanism.

---

## Deployment Strategy #1 – Raw OpenShift Deployment (Pipeline-driven)

This deployment represents a **traditional CI/CD workflow** using declarative Kubernetes manifests.

### CI – GitHub Actions
- Builds the application container image on every commit  
- Pushes the image to **Docker Hub**  
- Uses **immutable image tags** derived from the commit  
- Automatically updates `k8s/api-deployment.yaml` with the new tag  

This ensures reproducibility and avoids reliance on mutable image tags like `latest`.

### CD – Tekton Pipeline (OpenShift UI)

The Tekton pipeline was created using the OpenShift Developer UI and consists of:

1. **git-clone**  
   - Clones the repository into a shared workspace  
2. **oc-apply-k8s**  
   - Applies all manifests from the `k8s/` directory  

#### Resources Deployed
- `readinglist-api` Deployment  
- Service  
- Route  
- ConfigMap  
- Secret  
- PostgreSQL Deployment + PVC  

This pipeline represents a standard GitOps-style approach using raw Kubernetes YAML.

---

## Autoscaling and Resource Management

For the raw deployment, I configured:

- CPU and memory **requests & limits**  
- A **Horizontal Pod Autoscaler** (CPU-based)  

Using controlled load testing, I demonstrated:

- Initial pod count  
- CPU utilization increase  
- Automatic scaling up to the defined maximum  
- Scaling behavior observable via CLI and UI  

This portion of the project demonstrates operational knowledge around performance, scaling, and resource efficiency.

---

## Deployment Strategy #2 – Helm-managed Deployment

The second deployment path uses **Helm** to package and manage the application as a release.

### Helm Chart
- Located at `helm/readinglist`
- Templates include:
  - Deployment
  - Service
  - Route
  - ConfigMap
  - Secret
- `values.yaml` controls:
  - Replica count
  - Image repository
  - Image tag
  - Environment name
  - Banner message

The chart is stored in Git and installed via Helm CLI due to limitations in the Developer Sandbox UI.

### Helm Release
- Release name: `rl-helm`
- Installed into the same namespace as the raw deployment
- Fully visible and manageable from the OpenShift Console

The Helm deployment creates a separate application instance (`rl-helm-api`) that:
- Uses the **same container image**
- Connects to the **same PostgreSQL database**
- Is managed independently from the Tekton pipeline

---

## Helm Capabilities Demonstrated

- Scaling via **Helm upgrade** (e.g., 2 → 5 replicas)  
- Config changes via **Helm values**  
- Controlled rollouts through Helm-managed releases  
- Ability to roll back to previous revisions if needed  

The Helm deployment intentionally controls its own image tag to preserve release integrity and enable deterministic upgrades.

---

## Configuration Management & Runtime Behavior

### Raw Deployment Configuration
- Configuration provided via a Kubernetes ConfigMap  
- Example banner:  Reading List – Raw Deployment

### Helm Deployment Configuration
- Configuration driven through Helm values  
- Example banner:  Reading List – Helm Deployment

The application reads configuration from environment variables at runtime, allowing behavior to differ between deployments **without code changes**.

---

## Shared Backend Pattern

Both deployments:
- Use the same PostgreSQL Service  
- Share the same schema and data  
- Operate independently at the application layer  

This allows live demonstration that:
- Adding data in one deployment immediately reflects in the other  
- Deployment strategy does not affect data integrity  
- The application is properly stateless  

---

## Image Management and Versioning

- The raw deployment uses **explicit, immutable image tags** provided by CI  
- The Helm deployment is upgraded manually to a specific tag when promoting a version  

This design intentionally separates responsibilities:
- CI determines *what* image to build  
- Helm determines *when* that image is promoted  

This mirrors real-world production practices and avoids unsafe reliance on mutable tags.

---

## OpenShift Features Utilized

This project exercises the following OpenShift capabilities:

- Developer vs Administrator perspectives  
- Projects and namespaces  
- Deployments, Services, Routes  
- ConfigMaps and Secrets  
- PersistentVolumeClaims  
- Security Context Constraints (non-root containers)  
- Tekton Pipelines and Tasks  
- Helm charts and releases  
- Horizontal Pod Autoscaling  
- Resource requests and limits  
- Observability through logs, events, and scaling behavior  
- CLI and UI workflows  
- Platform limitations and RBAC constraints in sandbox environments  

---

## Summary

This capstone demonstrates not just how to deploy an application to OpenShift, but how to **reason about deployment strategy**, **separate concerns**, and **operate within platform constraints**.

By deploying the same application in multiple ways, integrating CI/CD tooling, applying autoscaling, and managing configuration correctly, I’ve shown an understanding of OpenShift as a platform — not just Kubernetes YAML.


