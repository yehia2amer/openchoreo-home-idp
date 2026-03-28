Directory Structure:
---
├── 📁 .devcontainer
│   ├── 📄 devcontainer.json
│   └── 📄 post-install.sh
├── 📁 .github
│   ├── 📁 actions
│   │   └── 📁 setup-go
│   │       └── 📄 action.yml
│   ├── 📁 workflows
│   │   ├── 📄 backport.yml
│   │   ├── 📄 build-and-test.yml
│   │   ├── 📄 cleanup-artifacts.yml
│   │   ├── 📄 codeql.yml
│   │   ├── 📄 lint-pr.yml
│   │   ├── 📄 release.yml
│   │   ├── 📄 scorecard.yml
│   │   ├── 📄 stale.yml
│   │   └── 📄 test-e2e.yml
│   ├── 📄 codecov.yml
│   ├── 📄 CODEOWNERS
│   ├── 📄 dco.yml
│   ├── 📄 dependabot.yml
│   └── 📄 pull_request_template.md
├── 📁 api
│   └── 📁 v1alpha1
│       ├── 📄 authzrole_types.go
│       ├── 📄 authzrolebinding_types.go
│       ├── 📄 clusterauthzrole_types.go
│       ├── 📄 clusterauthzrolebinding_types.go
│       ├── 📄 clustercomponenttype_types.go
│       ├── 📄 clusterdataplane_types.go
│       ├── 📄 clusterobservabilityplane_types.go
│       ├── 📄 clustertrait_types.go
│       ├── 📄 clusterworkflow_types.go
│       ├── 📄 clusterworkflowplane_types.go
│       ├── 📄 component_types.go
│       ├── 📄 componentrelease_types.go
│       ├── 📄 componenttype_types.go
│       ├── 📄 dataplane_types.go
│       ├── 📄 deploymentpipeline_types.go
│       ├── 📄 environment_types.go
│       ├── 📄 groupversion_info.go
│       ├── 📄 observabilityalertrule_types.go
│       ├── 📄 observabilityalertsnotificationchannel_types.go
│       ├── 📄 observabilityplane_types.go
│       ├── 📄 project_types.go
│       ├── 📄 releasebinding_types.go
│       ├── 📄 renderedrelease_types.go
│       ├── 📄 secretreference_types.go
│       ├── 📄 trait_types.go
│       ├── 📄 types.go
│       ├── 📄 workflow_types.go
│       ├── 📄 workflowplane_types.go
│       ├── 📄 workflowrun_types.go
│       ├── 📄 workload_types.go
│       └── 📄 zz_generated.deepcopy.go
├── 📁 cmd
│   ├── 📁 cluster-agent
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 kubernetes.go
│   │   └── 📄 main.go
│   ├── 📁 cluster-gateway
│   │   ├── 📄 Dockerfile
│   │   └── 📄 main.go
│   ├── 📁 observer
│   │   ├── 📄 auth-config.yaml
│   │   ├── 📄 Dockerfile
│   │   └── 📄 main.go
│   ├── 📁 occ
│   │   ├── 📄 Dockerfile
│   │   └── 📄 main.go
│   ├── 📁 openchoreo-api
│   │   ├── 📄 config.yaml
│   │   ├── 📄 Dockerfile
│   │   └── 📄 main.go
│   └── 📄 main.go
├── 📁 config
│   ├── 📁 certmanager
│   │   ├── 📄 certificate.yaml
│   │   ├── 📄 kustomization.yaml
│   │   └── 📄 kustomizeconfig.yaml
│   ├── 📁 crd
│   │   ├── 📁 bases
│   │   │   ├── 📄 openchoreo.dev_authzrolebindings.yaml
│   │   │   ├── 📄 openchoreo.dev_authzroles.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterauthzrolebindings.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterauthzroles.yaml
│   │   │   ├── 📄 openchoreo.dev_clustercomponenttypes.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterdataplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterobservabilityplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_clustertraits.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterworkflowplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_clusterworkflows.yaml
│   │   │   ├── 📄 openchoreo.dev_componentreleases.yaml
│   │   │   ├── 📄 openchoreo.dev_components.yaml
│   │   │   ├── 📄 openchoreo.dev_componenttypes.yaml
│   │   │   ├── 📄 openchoreo.dev_dataplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_deploymentpipelines.yaml
│   │   │   ├── 📄 openchoreo.dev_environments.yaml
│   │   │   ├── 📄 openchoreo.dev_observabilityalertrules.yaml
│   │   │   ├── 📄 openchoreo.dev_observabilityalertsnotificationchannels.yaml
│   │   │   ├── 📄 openchoreo.dev_observabilityplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_projects.yaml
│   │   │   ├── 📄 openchoreo.dev_releasebindings.yaml
│   │   │   ├── 📄 openchoreo.dev_renderedreleases.yaml
│   │   │   ├── 📄 openchoreo.dev_secretreferences.yaml
│   │   │   ├── 📄 openchoreo.dev_traits.yaml
│   │   │   ├── 📄 openchoreo.dev_workflowplanes.yaml
│   │   │   ├── 📄 openchoreo.dev_workflowruns.yaml
│   │   │   ├── 📄 openchoreo.dev_workflows.yaml
│   │   │   └── 📄 openchoreo.dev_workloads.yaml
│   │   ├── 📄 crd.go
│   │   ├── 📄 kustomization.yaml
│   │   └── 📄 kustomizeconfig.yaml
│   ├── 📁 default
│   │   ├── 📄 kustomization.yaml
│   │   ├── 📄 manager_metrics_patch.yaml
│   │   ├── 📄 manager_webhook_patch.yaml
│   │   └── 📄 metrics_service.yaml
│   ├── 📁 manager
│   │   ├── 📄 kustomization.yaml
│   │   └── 📄 manager.yaml
│   ├── 📁 network-policy
│   │   ├── 📄 allow-metrics-traffic.yaml
│   │   ├── 📄 allow-webhook-traffic.yaml
│   │   └── 📄 kustomization.yaml
│   ├── 📁 prometheus
│   │   ├── 📄 kustomization.yaml
│   │   └── 📄 monitor.yaml
│   ├── 📁 rbac
│   │   ├── 📄 authzrole_admin_role.yaml
│   │   ├── 📄 authzrole_editor_role.yaml
│   │   ├── 📄 authzrole_viewer_role.yaml
│   │   ├── 📄 authzrolebinding_admin_role.yaml
│   │   ├── 📄 authzrolebinding_editor_role.yaml
│   │   ├── 📄 authzrolebinding_viewer_role.yaml
│   │   ├── 📄 clusterauthzrole_admin_role.yaml
│   │   ├── 📄 clusterauthzrole_editor_role.yaml
│   │   ├── 📄 clusterauthzrole_viewer_role.yaml
│   │   ├── 📄 clusterauthzrolebinding_admin_role.yaml
│   │   ├── 📄 clusterauthzrolebinding_editor_role.yaml
│   │   ├── 📄 clusterauthzrolebinding_viewer_role.yaml
│   │   ├── 📄 clustercomponenttype_admin_role.yaml
│   │   ├── 📄 clustercomponenttype_editor_role.yaml
│   │   ├── 📄 clustercomponenttype_viewer_role.yaml
│   │   ├── 📄 clusterdataplane_admin_role.yaml
│   │   ├── 📄 clusterdataplane_editor_role.yaml
│   │   ├── 📄 clusterdataplane_viewer_role.yaml
│   │   ├── 📄 clusterobservabilityplane_admin_role.yaml
│   │   ├── 📄 clusterobservabilityplane_editor_role.yaml
│   │   ├── 📄 clusterobservabilityplane_viewer_role.yaml
│   │   ├── 📄 clustertrait_admin_role.yaml
│   │   ├── 📄 clustertrait_editor_role.yaml
│   │   ├── 📄 clustertrait_viewer_role.yaml
│   │   ├── 📄 clusterworkflow_admin_role.yaml
│   │   ├── 📄 clusterworkflow_editor_role.yaml
│   │   ├── 📄 clusterworkflow_viewer_role.yaml
│   │   ├── 📄 clusterworkflowplane_admin_role.yaml
│   │   ├── 📄 clusterworkflowplane_editor_role.yaml
│   │   ├── 📄 clusterworkflowplane_viewer_role.yaml
│   │   ├── 📄 component_editor_role.yaml
│   │   ├── 📄 component_viewer_role.yaml
│   │   ├── 📄 componentrelease_editor_role.yaml
│   │   ├── 📄 componentrelease_viewer_role.yaml
│   │   ├── 📄 componenttype_admin_role.yaml
│   │   ├── 📄 componenttype_editor_role.yaml
│   │   ├── 📄 componenttype_viewer_role.yaml
│   │   ├── 📄 dataplane_editor_role.yaml
│   │   ├── 📄 dataplane_viewer_role.yaml
│   │   ├── 📄 deploymentpipeline_editor_role.yaml
│   │   ├── 📄 deploymentpipeline_viewer_role.yaml
│   │   ├── 📄 environment_editor_role.yaml
│   │   ├── 📄 environment_viewer_role.yaml
│   │   ├── 📄 kustomization.yaml
│   │   ├── 📄 leader_election_role_binding.yaml
│   │   ├── 📄 leader_election_role.yaml
│   │   ├── 📄 metrics_auth_role_binding.yaml
│   │   ├── 📄 metrics_auth_role.yaml
│   │   ├── 📄 metrics_reader_role.yaml
│   │   ├── 📄 namespace_editor_role.yaml
│   │   ├── 📄 namespace_viewer_role.yaml
│   │   ├── 📄 observabilityalertrule_admin_role.yaml
│   │   ├── 📄 observabilityalertrule_editor_role.yaml
│   │   ├── 📄 observabilityalertrule_viewer_role.yaml
│   │   ├── 📄 observabilityalertsnotificationchannel_admin_role.yaml
│   │   ├── 📄 observabilityalertsnotificationchannel_editor_role.yaml
│   │   ├── 📄 observabilityalertsnotificationchannel_viewer_role.yaml
│   │   ├── 📄 observabilityplane_admin_role.yaml
│   │   ├── 📄 observabilityplane_editor_role.yaml
│   │   ├── 📄 observabilityplane_viewer_role.yaml
│   │   ├── 📄 project_editor_role.yaml
│   │   ├── 📄 project_viewer_role.yaml
│   │   ├── 📄 releasebinding_editor_role.yaml
│   │   ├── 📄 releasebinding_viewer_role.yaml
│   │   ├── 📄 renderedrelease_editor_role.yaml
│   │   ├── 📄 renderedrelease_viewer_role.yaml
│   │   ├── 📄 role_binding.yaml
│   │   ├── 📄 role.yaml
│   │   ├── 📄 secretreference_editor_role.yaml
│   │   ├── 📄 secretreference_viewer_role.yaml
│   │   ├── 📄 service_account.yaml
│   │   ├── 📄 trait_admin_role.yaml
│   │   ├── 📄 trait_editor_role.yaml
│   │   ├── 📄 trait_viewer_role.yaml
│   │   ├── 📄 workflow_admin_role.yaml
│   │   ├── 📄 workflow_editor_role.yaml
│   │   ├── 📄 workflow_viewer_role.yaml
│   │   ├── 📄 workflowplane_admin_role.yaml
│   │   ├── 📄 workflowplane_editor_role.yaml
│   │   ├── 📄 workflowplane_viewer_role.yaml
│   │   ├── 📄 workflowrun_admin_role.yaml
│   │   ├── 📄 workflowrun_editor_role.yaml
│   │   ├── 📄 workflowrun_viewer_role.yaml
│   │   ├── 📄 workload_editor_role.yaml
│   │   └── 📄 workload_viewer_role.yaml
│   ├── 📁 samples
│   │   ├── 📄 kustomization.yaml
│   │   ├── 📄 openchoreo_v1alpha1_clustercomponenttype.yaml
│   │   ├── 📄 openchoreo_v1alpha1_clusterdataplane.yaml
│   │   ├── 📄 openchoreo_v1alpha1_clusterobservabilityplane.yaml
│   │   ├── 📄 openchoreo_v1alpha1_clustertrait.yaml
│   │   ├── 📄 openchoreo_v1alpha1_clusterworkflowplane.yaml
│   │   ├── 📄 openchoreo_v1alpha1_component.yaml
│   │   ├── 📄 openchoreo_v1alpha1_componentrelease.yaml
│   │   ├── 📄 openchoreo_v1alpha1_componenttype.yaml
│   │   ├── 📄 openchoreo_v1alpha1_dataplane.yaml
│   │   ├── 📄 openchoreo_v1alpha1_deploymentpipeline.yaml
│   │   ├── 📄 openchoreo_v1alpha1_environment.yaml
│   │   ├── 📄 openchoreo_v1alpha1_project.yaml
│   │   ├── 📄 openchoreo_v1alpha1_releasebinding.yaml
│   │   ├── 📄 openchoreo_v1alpha1_renderedrelease.yaml
│   │   ├── 📄 openchoreo_v1alpha1_secretreference.yaml
│   │   ├── 📄 openchoreo_v1alpha1_trait.yaml
│   │   ├── 📄 openchoreo_v1alpha1_workflow.yaml
│   │   ├── 📄 openchoreo_v1alpha1_workflowplane.yaml
│   │   ├── 📄 openchoreo_v1alpha1_workflowrun.yaml
│   │   ├── 📄 openchoreo_v1alpha1_workload.yaml
│   │   ├── 📄 v1alpha1_authzrole.yaml
│   │   ├── 📄 v1alpha1_authzrolebinding.yaml
│   │   ├── 📄 v1alpha1_clusterauthzrole.yaml
│   │   ├── 📄 v1alpha1_clusterauthzrolebinding.yaml
│   │   ├── 📄 v1alpha1_observabilityalertrule.yaml
│   │   ├── 📄 v1alpha1_observabilityalertsnotificationchannel.yaml
│   │   └── 📄 v1alpha1_observabilityplane.yaml
│   └── 📁 webhook
│       ├── 📄 kustomization.yaml
│       ├── 📄 kustomizeconfig.yaml
│       ├── 📄 manifests.yaml
│       └── 📄 service.yaml
├── 📁 docs
│   ├── 📁 contributors
│   │   ├── 📄 adding-new-crd.md
│   │   ├── 📄 adding-new-mcp-tools.md
│   │   ├── 📄 build-engines.md
│   │   ├── 📄 contribute.md
│   │   ├── 📄 development-process.md
│   │   ├── 📄 github_workflow.md
│   │   ├── 📄 README.md
│   │   └── 📄 release.md
│   ├── 📁 crds
│   │   ├── 📄 README.md
│   │   └── 📄 renderedrelease.md
│   ├── 📁 images
│   │   ├── 📄 openchoreo-architecture-diagram.png
│   │   ├── 📄 openchoreo-cell-runtime-view.png
│   │   ├── 📄 openchoreo-ddd-to-cell-mapping.png
│   │   ├── 📄 openchoreo-development-abstractions.png
│   │   ├── 📄 openchoreo-diagram-v1-with-borders.png
│   │   ├── 📄 openchoreo-diagram-v1.png
│   │   ├── 📄 openchoreo-diagram-v1.webp
│   │   ├── 📄 openchoreo-horizontal-color.png
│   │   ├── 📄 openchoreo-overall-architecture.png
│   │   └── 📄 openchoreo-platform-abstractions.png
│   ├── 📁 proposals
│   │   ├── 📁 0159-assets
│   │   │   ├── 📄 agent-based.png
│   │   │   ├── 📄 direct-access.png
│   │   │   └── 📄 gitops.png
│   │   ├── 📄 0142-standardize-build-conditions.md
│   │   ├── 📄 0159-control-plane-data-plane-separation.md
│   │   ├── 📄 0186-integrate-external-idp.md
│   │   ├── 📄 0200-openchoreo-developer-concepts.md
│   │   ├── 📄 0245-introduce-build-plane.md
│   │   ├── 📄 0482-modular-architecture-proposal.md
│   │   ├── 📄 0537-introduce-component-type-definitions.md
│   │   ├── 📄 README.md
│   │   └── 📄 xxxx-proposal-template.md
│   ├── 📁 templating
│   │   ├── 📄 configuration_helpers.md
│   │   ├── 📄 context.md
│   │   ├── 📄 openapiv3-schema.md
│   │   ├── 📄 patching.md
│   │   ├── 📄 templating.md
│   │   └── 📄 validations.md
│   ├── 📄 configure-controlplane-mcp-server.md
│   └── 📄 resource-kind-reference-guide.md
├── 📁 hack
│   └── 📄 boilerplate.go.txt
├── 📁 install
│   ├── 📁 base-images
│   │   ├── 📄 Dockerfile
│   │   └── 📄 ubuntu.Dockerfile
│   ├── 📁 helm
│   │   ├── 📁 openchoreo-control-plane
│   │   │   ├── 📁 crds
│   │   │   │   ├── 📄 openchoreo.dev_authzrolebindings.yaml
│   │   │   │   ├── 📄 openchoreo.dev_authzroles.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterauthzrolebindings.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterauthzroles.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clustercomponenttypes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterdataplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterobservabilityplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clustertraits.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterworkflowplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_clusterworkflows.yaml
│   │   │   │   ├── 📄 openchoreo.dev_componentreleases.yaml
│   │   │   │   ├── 📄 openchoreo.dev_components.yaml
│   │   │   │   ├── 📄 openchoreo.dev_componenttypes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_dataplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_deploymentpipelines.yaml
│   │   │   │   ├── 📄 openchoreo.dev_environments.yaml
│   │   │   │   ├── 📄 openchoreo.dev_observabilityalertsnotificationchannels.yaml
│   │   │   │   ├── 📄 openchoreo.dev_observabilityplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_projects.yaml
│   │   │   │   ├── 📄 openchoreo.dev_releasebindings.yaml
│   │   │   │   ├── 📄 openchoreo.dev_renderedreleases.yaml
│   │   │   │   ├── 📄 openchoreo.dev_secretreferences.yaml
│   │   │   │   ├── 📄 openchoreo.dev_traits.yaml
│   │   │   │   ├── 📄 openchoreo.dev_workflowplanes.yaml
│   │   │   │   ├── 📄 openchoreo.dev_workflowruns.yaml
│   │   │   │   ├── 📄 openchoreo.dev_workflows.yaml
│   │   │   │   └── 📄 openchoreo.dev_workloads.yaml
│   │   │   ├── 📁 templates
│   │   │   │   ├── 📁 authz
│   │   │   │   │   └── 📄 bootstrap-authz.yaml
│   │   │   │   ├── 📁 backstage
│   │   │   │   │   ├── 📄 configmap-ci.yaml
│   │   │   │   │   ├── 📄 configmap-csp.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 hpa.yaml
│   │   │   │   │   ├── 📄 httproute.yaml
│   │   │   │   │   ├── 📄 networkpolicy.yaml
│   │   │   │   │   ├── 📄 pdb.yaml
│   │   │   │   │   ├── 📄 priorityclass.yaml
│   │   │   │   │   ├── 📄 pvc.yaml
│   │   │   │   │   ├── 📄 service.yaml
│   │   │   │   │   └── 📄 serviceaccount.yaml
│   │   │   │   ├── 📁 cluster-gateway
│   │   │   │   │   ├── 📄 ca-certificate.yaml
│   │   │   │   │   ├── 📄 ca-configmap-placeholder.yaml
│   │   │   │   │   ├── 📄 certificate.yaml
│   │   │   │   │   ├── 📄 clusterrole.yaml
│   │   │   │   │   ├── 📄 clusterrolebinding.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 issuer.yaml
│   │   │   │   │   ├── 📄 role.yaml
│   │   │   │   │   ├── 📄 rolebinding.yaml
│   │   │   │   │   ├── 📄 service.yaml
│   │   │   │   │   ├── 📄 serviceaccount.yaml
│   │   │   │   │   └── 📄 tlsroute.yaml
│   │   │   │   ├── 📁 controller-manager
│   │   │   │   │   ├── 📄 controller-manager-role-binding.yaml
│   │   │   │   │   ├── 📄 controller-manager-role.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 hpa.yaml
│   │   │   │   │   ├── 📄 leader-election-role-binding.yaml
│   │   │   │   │   ├── 📄 leader-election-role.yaml
│   │   │   │   │   ├── 📄 mutating-webhook-configuration.yaml
│   │   │   │   │   ├── 📄 networkpolicy.yaml
│   │   │   │   │   ├── 📄 pdb.yaml
│   │   │   │   │   ├── 📄 priorityclass.yaml
│   │   │   │   │   ├── 📄 selfsigned-issuer.yaml
│   │   │   │   │   ├── 📄 service-account.yaml
│   │   │   │   │   ├── 📄 servicemonitor.yaml
│   │   │   │   │   ├── 📄 validating-webhook-configuration.yaml
│   │   │   │   │   ├── 📄 webhook-server-cert.yaml
│   │   │   │   │   └── 📄 webhook-service.yaml
│   │   │   │   ├── 📁 gateway
│   │   │   │   │   └── 📄 gateway.yaml
│   │   │   │   ├── 📁 openchoreo-api
│   │   │   │   │   ├── 📄 clusterrole.yaml
│   │   │   │   │   ├── 📄 clusterrolebinding.yaml
│   │   │   │   │   ├── 📄 configmap.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 hpa.yaml
│   │   │   │   │   ├── 📄 httproute.yaml
│   │   │   │   │   ├── 📄 networkpolicy.yaml
│   │   │   │   │   ├── 📄 pdb.yaml
│   │   │   │   │   ├── 📄 priorityclass.yaml
│   │   │   │   │   ├── 📄 service.yaml
│   │   │   │   │   ├── 📄 serviceaccount.yaml
│   │   │   │   │   ├── 📄 servicemonitor.yaml
│   │   │   │   │   └── 📄 traffic-policy.yaml
│   │   │   │   ├── 📄 _helpers.tpl
│   │   │   │   └── 📄 NOTES.txt
│   │   │   ├── 📄 .helmignore
│   │   │   ├── 📄 Chart.yaml
│   │   │   ├── 📄 values.schema.json
│   │   │   └── 📄 values.yaml
│   │   ├── 📁 openchoreo-data-plane
│   │   │   ├── 📁 templates
│   │   │   │   ├── 📁 cluster-agent
│   │   │   │   │   ├── 📄 certificate.yaml
│   │   │   │   │   ├── 📄 clusterrole.yaml
│   │   │   │   │   ├── 📄 clusterrolebinding.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 issuer.yaml
│   │   │   │   │   ├── 📄 pdb.yaml
│   │   │   │   │   └── 📄 serviceaccount.yaml
│   │   │   │   ├── 📁 gateway
│   │   │   │   │   └── 📄 gateway.yaml
│   │   │   │   ├── 📁 security
│   │   │   │   │   ├── 📄 cert-issuer.yaml
│   │   │   │   │   └── 📄 serving-cert.yaml
│   │   │   │   ├── 📄 _helpers.tpl
│   │   │   │   └── 📄 NOTES.txt
│   │   │   ├── 📄 .helmignore
│   │   │   ├── 📄 Chart.lock
│   │   │   ├── 📄 Chart.yaml
│   │   │   ├── 📄 values.schema.json
│   │   │   └── 📄 values.yaml
│   │   ├── 📁 openchoreo-observability-plane
│   │   │   ├── 📁 crds
│   │   │   │   └── 📄 openchoreo.dev_observabilityalertrules.yaml
│   │   │   ├── 📁 templates
│   │   │   │   ├── 📁 ai-rca-agent
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 http-route.yaml
│   │   │   │   │   ├── 📄 pvc.yaml
│   │   │   │   │   ├── 📄 rca-agent-config.yaml
│   │   │   │   │   └── 📄 service.yaml
│   │   │   │   ├── 📁 cluster-agent
│   │   │   │   │   ├── 📄 certificate.yaml
│   │   │   │   │   ├── 📄 clusterrole.yaml
│   │   │   │   │   ├── 📄 clusterrolebinding.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   ├── 📄 issuer.yaml
│   │   │   │   │   ├── 📄 pdb.yaml
│   │   │   │   │   └── 📄 serviceaccount.yaml
│   │   │   │   ├── 📁 controller-manager
│   │   │   │   │   ├── 📄 clusterrolebinding.yaml
│   │   │   │   │   ├── 📄 controller-manager-role.yaml
│   │   │   │   │   ├── 📄 deployment.yaml
│   │   │   │   │   └── 📄 serviceaccount.yaml
│   │   │   │   ├── 📁 gateway
│   │   │   │   │   └── 📄 gateway.yaml
│   │   │   │   ├── 📁 observer
│   │   │   │   │   ├── 📄 http-route.yaml
│   │   │   │   │   ├── 📄 observer-alerts-pvc.yaml
│   │   │   │   │   ├── 📄 observer-auth-configmap.yaml
│   │   │   │   │   ├── 📄 observer-config.yaml
│   │   │   │   │   ├── 📄 observer-deployment.yaml
│   │   │   │   │   ├── 📄 observer-internal-service.yaml
│   │   │   │   │   ├── 📄 observer-opensearch-secret.yaml
│   │   │   │   │   ├── 📄 observer-role.yaml
│   │   │   │   │   ├── 📄 observer-rolebinding.yaml
│   │   │   │   │   ├── 📄 observer-service-account.yaml
│   │   │   │   │   ├── 📄 observer-service.yaml
│   │   │   │   │   └── 📄 traffic-policy.yaml
│   │   │   │   ├── 📁 tls
│   │   │   │   │   ├── 📄 certificate.yaml
│   │   │   │   │   └── 📄 issuer.yaml
│   │   │   │   └── 📄 _helpers.tpl
│   │   │   ├── 📄 Chart.yaml
│   │   │   ├── 📄 values.schema.json
│   │   │   └── 📄 values.yaml
│   │   └── 📁 openchoreo-workflow-plane
│   │       ├── 📁 templates
│   │       │   ├── 📁 cluster-agent
│   │       │   │   ├── 📄 certificate.yaml
│   │       │   │   ├── 📄 clusterrole.yaml
│   │       │   │   ├── 📄 clusterrolebinding.yaml
│   │       │   │   ├── 📄 deployment.yaml
│   │       │   │   ├── 📄 issuer.yaml
│   │       │   │   ├── 📄 pdb.yaml
│   │       │   │   └── 📄 serviceaccount.yaml
│   │       │   ├── 📄 _helpers.tpl
│   │       │   └── 📄 NOTES.txt
│   │       ├── 📄 .helmignore
│   │       ├── 📄 Chart.lock
│   │       ├── 📄 Chart.yaml
│   │       ├── 📄 values.schema.json
│   │       └── 📄 values.yaml
│   ├── 📁 init
│   │   └── 📁 observability
│   │       └── 📁 opensearch
│   │           ├── 📄 Dockerfile
│   │           └── 📄 setup-opensearch-cluster.sh
│   ├── 📁 k3d
│   │   ├── 📁 common
│   │   │   ├── 📄 coredns-custom.yaml
│   │   │   ├── 📄 gateway-tmp-volume-patch.json
│   │   │   ├── 📄 push-buildpack-cache-images.yaml
│   │   │   ├── 📄 values-openbao.yaml
│   │   │   └── 📄 values-thunder.yaml
│   │   ├── 📁 multi-cluster
│   │   │   ├── 📄 config-cp.yaml
│   │   │   ├── 📄 config-dp.yaml
│   │   │   ├── 📄 config-op.yaml
│   │   │   ├── 📄 config-wp.yaml
│   │   │   ├── 📄 README.md
│   │   │   ├── 📄 values-cp.yaml
│   │   │   ├── 📄 values-dp.yaml
│   │   │   ├── 📄 values-op.yaml
│   │   │   ├── 📄 values-registry.yaml
│   │   │   └── 📄 values-wp.yaml
│   │   ├── 📁 registry-cache
│   │   │   ├── 📄 compose.yaml
│   │   │   ├── 📄 list-cached.sh
│   │   │   ├── 📄 purge-cache.sh
│   │   │   └── 📄 README.md
│   │   ├── 📁 single-cluster
│   │   │   ├── 📄 config.yaml
│   │   │   ├── 📄 README.md
│   │   │   ├── 📄 values-cp.yaml
│   │   │   ├── 📄 values-dp.yaml
│   │   │   ├── 📄 values-op.yaml
│   │   │   ├── 📄 values-registry.yaml
│   │   │   └── 📄 values-wp.yaml
│   │   ├── 📄 k3d-observability-plane.sh
│   │   ├── 📄 k3d-prerequisites.sh
│   │   ├── 📄 preload-images.sh
│   │   └── 📄 README.md
│   ├── 📁 prerequisites
│   │   └── 📁 openbao
│   │       └── 📄 setup.sh
│   ├── 📁 quick-start
│   │   ├── 📄 .bash_profile
│   │   ├── 📄 .bashrc
│   │   ├── 📄 .config.sh
│   │   ├── 📄 .entrypoint.sh
│   │   ├── 📄 .helpers.sh
│   │   ├── 📄 .values-cp.yaml
│   │   ├── 📄 .values-dp.yaml
│   │   ├── 📄 .values-op.yaml
│   │   ├── 📄 .values-registry.yaml
│   │   ├── 📄 .values-wp.yaml
│   │   ├── 📄 .welcome
│   │   ├── 📄 build-deploy-greeter.sh
│   │   ├── 📄 check-status.sh
│   │   ├── 📄 deploy-gcp-demo.sh
│   │   ├── 📄 deploy-react-starter.sh
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 install.sh
│   │   ├── 📄 occ-login.sh
│   │   ├── 📄 README.md
│   │   ├── 📄 uninstall.sh
│   │   └── 📄 validate-installation.sh
│   ├── 📄 occ-install.sh
│   └── 📄 occ-uninstall.sh
├── 📁 internal
│   ├── 📁 authz
│   │   ├── 📁 casbin
│   │   │   ├── 📄 enforcer.go
│   │   │   ├── 📄 helpers_test.go
│   │   │   ├── 📄 helpers.go
│   │   │   ├── 📄 k8s_watcher_test.go
│   │   │   ├── 📄 k8s_watcher.go
│   │   │   ├── 📄 pap_test.go
│   │   │   ├── 📄 pap.go
│   │   │   ├── 📄 pdp_test.go
│   │   │   ├── 📄 pdp.go
│   │   │   └── 📄 rbac_model.conf
│   │   ├── 📁 core
│   │   │   ├── 📄 actions_test.go
│   │   │   ├── 📄 actions.go
│   │   │   ├── 📄 converter.go
│   │   │   ├── 📄 interface.go
│   │   │   └── 📄 types.go
│   │   ├── 📄 disabled_authorizer_test.go
│   │   ├── 📄 disabled_authorizer.go
│   │   └── 📄 init.go
│   ├── 📁 clients
│   │   ├── 📁 gateway
│   │   │   ├── 📄 client_test.go
│   │   │   └── 📄 client.go
│   │   └── 📁 kubernetes
│   │       ├── 📄 client.go
│   │       └── 📄 proxy_client.go
│   ├── 📁 clone
│   │   └── 📄 deepcopy.go
│   ├── 📁 cluster-agent
│   │   ├── 📁 messaging
│   │   │   ├── 📄 errors.go
│   │   │   └── 📄 types.go
│   │   ├── 📄 agent.go
│   │   ├── 📄 config.go
│   │   └── 📄 router.go
│   ├── 📁 cluster-gateway
│   │   ├── 📄 config.go
│   │   ├── 📄 connection_manager.go
│   │   ├── 📄 plane_api.go
│   │   ├── 📄 plane_client_ca_test.go
│   │   ├── 📄 plane_client_ca.go
│   │   ├── 📄 server.go
│   │   └── 📄 validator.go
│   ├── 📁 cmdutil
│   │   ├── 📄 duration_test.go
│   │   ├── 📄 duration.go
│   │   ├── 📄 env.go
│   │   └── 📄 logger.go
│   ├── 📁 componentrelease
│   │   ├── 📄 builder_test.go
│   │   └── 📄 builder.go
│   ├── 📁 config
│   │   ├── 📁 testdata
│   │   │   └── 📄 test_config.yaml
│   │   ├── 📄 loader_test.go
│   │   ├── 📄 loader.go
│   │   ├── 📄 validation_test.go
│   │   └── 📄 validation.go
│   ├── 📁 controller
│   │   ├── 📁 clustercomponenttype
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 clusterdataplane
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_gateway_test.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_rbac.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 clusterobservabilityplane
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 clustertrait
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 clusterworkflow
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 clusterworkflowplane
│   │   │   ├── 📄 controller_gateway_test.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 component
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_hash_test.go
│   │   │   ├── 📄 controller_hash.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 componentrelease
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 componenttype
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 dataplane
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_gateway_test.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_rbac.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 deploymentpipeline
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 environment
│   │   │   ├── 📁 integrations
│   │   │   │   └── 📁 kubernetes
│   │   │   │       └── 📄 namespaces_handler.go
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 observabilityalertrule
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 observabilityalertsnotificationchannel
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 observabilityplane
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 project
│   │   │   ├── 📁 integrations
│   │   │   │   └── 📁 kubernetes
│   │   │   │       └── 📄 namespace_handler.go
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_rbac.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   ├── 📄 project_context.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 releasebinding
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_connections.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_status.go
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_watch.go
│   │   │   ├── 📄 controller.go
│   │   │   ├── 📄 endpoint_resolve_test.go
│   │   │   ├── 📄 endpoint_resolve.go
│   │   │   ├── 📄 suite_test.go
│   │   │   └── 📄 workload_type.go
│   │   ├── 📁 renderedrelease
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_status.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 secretreference
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 testutils
│   │   │   ├── 📁 testgateway
│   │   │   │   └── 📄 fake_gateway.go
│   │   │   └── 📄 test_utils.go
│   │   ├── 📁 trait
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 workflow
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 workflowplane
│   │   │   ├── 📄 controller_gateway_test.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 workflowrun
│   │   │   ├── 📄 controller_conditions.go
│   │   │   ├── 📄 controller_finalize.go
│   │   │   ├── 📄 controller_integration_test.go
│   │   │   ├── 📄 controller_unit_test.go
│   │   │   ├── 📄 controller_validate.go
│   │   │   ├── 📄 controller.go
│   │   │   ├── 📄 externalref_test.go
│   │   │   ├── 📄 externalref.go
│   │   │   ├── 📄 run_engine.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📁 workload
│   │   │   ├── 📄 controller_test.go
│   │   │   ├── 📄 controller.go
│   │   │   └── 📄 suite_test.go
│   │   ├── 📄 annotations.go
│   │   ├── 📄 conditions_test.go
│   │   ├── 📄 conditions.go
│   │   ├── 📄 controller_common.go
│   │   ├── 📄 hierarchy.go
│   │   ├── 📄 metadata.go
│   │   ├── 📄 patch.go
│   │   ├── 📄 reference_test.go
│   │   ├── 📄 reference.go
│   │   └── 📄 watch.go
│   ├── 📁 dataplane
│   │   ├── 📁 kubernetes
│   │   │   ├── 📁 types
│   │   │   │   ├── 📁 argoproj.io
│   │   │   │   │   └── 📁 workflow
│   │   │   │   │       ├── 📁 v1alpha1
│   │   │   │   │       │   ├── 📄 cluster_workflow_template_types.go
│   │   │   │   │       │   ├── 📄 container_set_template_types.go
│   │   │   │   │       │   ├── 📄 data_types.go
│   │   │   │   │       │   ├── 📄 doc.go
│   │   │   │   │       │   ├── 📄 http_types.go
│   │   │   │   │       │   ├── 📄 item.go
│   │   │   │   │       │   ├── 📄 register.go
│   │   │   │   │       │   ├── 📄 workflow_types.go
│   │   │   │   │       │   └── 📄 zz_generated.deepcopy.go
│   │   │   │   │       ├── 📄 common.go
│   │   │   │   │       └── 📄 register.go
│   │   │   │   ├── 📁 cilium.io
│   │   │   │   │   └── 📁 v2
│   │   │   │   │       ├── 📄 register.go
│   │   │   │   │       ├── 📄 types.go
│   │   │   │   │       └── 📄 zz_generated.deepcopy.go
│   │   │   │   ├── 📁 externalsecrets
│   │   │   │   │   └── 📁 v1
│   │   │   │   │       ├── 📄 doc.go
│   │   │   │   │       ├── 📄 externalsecret_types.go
│   │   │   │   │       ├── 📄 register.go
│   │   │   │   │       └── 📄 zz_generated.deepcopy.go
│   │   │   │   ├── 📁 secretstorecsi
│   │   │   │   │   └── 📁 v1
│   │   │   │   │       ├── 📄 secretproviderclass_types.go
│   │   │   │   │       ├── 📄 secretproviderclasspodstatus_types.go
│   │   │   │   │       ├── 📄 zz_generated.deepcopy.go
│   │   │   │   │       └── 📄 zz_generated.register.go
│   │   │   │   ├── 📄 docs.go
│   │   │   │   └── 📄 README.md
│   │   │   ├── 📄 labels.go
│   │   │   ├── 📄 name_test.go
│   │   │   ├── 📄 name.go
│   │   │   ├── 📄 suite_test.go
│   │   │   └── 📄 system.go
│   │   ├── 📄 interfaces.go
│   │   └── 📄 types.go
│   ├── 📁 labels
│   │   └── 📄 labels.go
│   ├── 📁 logging
│   │   └── 📄 logging.go
│   ├── 📁 networkpolicy
│   │   ├── 📄 networkpolicy_test.go
│   │   └── 📄 networkpolicy.go
│   ├── 📁 observer
│   │   ├── 📁 adaptor
│   │   │   ├── 📄 logs_default.go
│   │   │   ├── 📄 traces_default_test.go
│   │   │   └── 📄 traces_default.go
│   │   ├── 📁 api
│   │   │   ├── 📁 gen
│   │   │   │   ├── 📄 client.gen.go
│   │   │   │   ├── 📄 models.gen.go
│   │   │   │   └── 📄 server.gen.go
│   │   │   ├── 📁 handlers
│   │   │   │   ├── 📄 alerts_query.go
│   │   │   │   ├── 📄 alerts.go
│   │   │   │   ├── 📄 handler.go
│   │   │   │   ├── 📄 health.go
│   │   │   │   ├── 📄 incidents_test.go
│   │   │   │   ├── 📄 logs.go
│   │   │   │   ├── 📄 metrics.go
│   │   │   │   ├── 📄 scope_auth_test.go
│   │   │   │   ├── 📄 traces_test.go
│   │   │   │   ├── 📄 traces.go
│   │   │   │   └── 📄 validations.go
│   │   │   ├── 📁 logsadapterclientgen
│   │   │   │   └── 📄 client.gen.go
│   │   │   ├── 📄 cfg-client.yaml
│   │   │   ├── 📄 cfg-logs-adapter-client.yaml
│   │   │   ├── 📄 cfg-models.yaml
│   │   │   └── 📄 cfg-server.yaml
│   │   ├── 📁 authz
│   │   │   ├── 📄 client.go
│   │   │   ├── 📄 constants.go
│   │   │   ├── 📄 errors.go
│   │   │   └── 📄 helpers.go
│   │   ├── 📁 clients
│   │   │   └── 📄 k8s.go
│   │   ├── 📁 config
│   │   │   ├── 📄 config_test.go
│   │   │   └── 📄 config.go
│   │   ├── 📁 httputil
│   │   │   └── 📄 json.go
│   │   ├── 📁 labels
│   │   │   └── 📄 constants.go
│   │   ├── 📁 mcp
│   │   │   ├── 📄 handlers.go
│   │   │   ├── 📄 helpers_test.go
│   │   │   ├── 📄 helpers.go
│   │   │   ├── 📄 server_test.go
│   │   │   └── 📄 server.go
│   │   ├── 📁 middleware
│   │   │   ├── 📄 middleware_test.go
│   │   │   └── 📄 middleware.go
│   │   ├── 📁 notifications
│   │   │   ├── 📄 email.go
│   │   │   ├── 📄 sender.go
│   │   │   └── 📄 webhook.go
│   │   ├── 📁 opensearch
│   │   │   ├── 📄 client.go
│   │   │   ├── 📄 process_test.go
│   │   │   ├── 📄 process.go
│   │   │   ├── 📄 queries_test.go
│   │   │   ├── 📄 queries_unit_test.go
│   │   │   ├── 📄 queries.go
│   │   │   └── 📄 types.go
│   │   ├── 📁 prometheus
│   │   │   ├── 📄 alertrules.go
│   │   │   ├── 📄 client_test.go
│   │   │   ├── 📄 client.go
│   │   │   ├── 📄 metrics_test.go
│   │   │   └── 📄 metrics.go
│   │   ├── 📁 service
│   │   │   ├── 📄 alert_incident_authz.go
│   │   │   ├── 📄 alerts_adapter.go
│   │   │   ├── 📄 alerts_crud_test.go
│   │   │   ├── 📄 alerts_duration_test.go
│   │   │   ├── 📄 alerts_helpers_test.go
│   │   │   ├── 📄 alerts_notifications_test.go
│   │   │   ├── 📄 alerts_query_test.go
│   │   │   ├── 📄 alerts_query.go
│   │   │   ├── 📄 alerts_routing_test.go
│   │   │   ├── 📄 alerts.go
│   │   │   ├── 📄 health.go
│   │   │   ├── 📄 interfaces.go
│   │   │   ├── 📄 logs_adapter.go
│   │   │   ├── 📄 logs_authz.go
│   │   │   ├── 📄 logs.go
│   │   │   ├── 📄 metrics_authz.go
│   │   │   ├── 📄 metrics.go
│   │   │   ├── 📄 notification_dispatch.go
│   │   │   ├── 📄 traces_authz.go
│   │   │   ├── 📄 traces_test.go
│   │   │   ├── 📄 traces.go
│   │   │   ├── 📄 tracing_adapter_test.go
│   │   │   ├── 📄 tracing_adapter.go
│   │   │   ├── 📄 uid_resolver_test.go
│   │   │   └── 📄 uid_resolver.go
│   │   ├── 📁 store
│   │   │   ├── 📁 alertentry
│   │   │   │   ├── 📄 sql_test.go
│   │   │   │   ├── 📄 sql.go
│   │   │   │   └── 📄 store.go
│   │   │   └── 📁 incidententry
│   │   │       ├── 📄 sql_test.go
│   │   │       ├── 📄 sql.go
│   │   │       └── 📄 store.go
│   │   └── 📁 types
│   │       ├── 📄 alerting.go
│   │       ├── 📄 errors.go
│   │       ├── 📄 logs.go
│   │       ├── 📄 metrics.go
│   │       ├── 📄 notifications.go
│   │       └── 📄 traces.go
│   ├── 📁 occ
│   │   ├── 📁 auth
│   │   │   ├── 📄 client_credential_test.go
│   │   │   ├── 📄 client_credential.go
│   │   │   ├── 📄 html.go
│   │   │   ├── 📄 oidc_config_test.go
│   │   │   ├── 📄 oidc_config.go
│   │   │   ├── 📄 pkce_test.go
│   │   │   ├── 📄 pkce.go
│   │   │   ├── 📄 server.go
│   │   │   ├── 📄 token_test.go
│   │   │   └── 📄 token.go
│   │   ├── 📁 browser
│   │   │   └── 📄 browser.go
│   │   ├── 📁 cmd
│   │   │   ├── 📁 apply
│   │   │   │   ├── 📄 apply_test.go
│   │   │   │   ├── 📄 apply.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 registry_test.go
│   │   │   │   └── 📄 registry.go
│   │   │   ├── 📁 authzrole
│   │   │   │   ├── 📄 authzrole.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 authzrolebinding
│   │   │   │   ├── 📄 authzrolebinding.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterauthzrole
│   │   │   │   ├── 📄 clusterauthzrole.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterauthzrolebinding
│   │   │   │   ├── 📄 clusterauthzrolebinding.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clustercomponenttype
│   │   │   │   ├── 📄 clustercomponenttype_test.go
│   │   │   │   ├── 📄 clustercomponenttype.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterdataplane
│   │   │   │   ├── 📄 clusterdataplane.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterobservabilityplane
│   │   │   │   ├── 📄 clusterobservabilityplane.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clustertrait
│   │   │   │   ├── 📄 clustertrait_test.go
│   │   │   │   ├── 📄 clustertrait.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterworkflow
│   │   │   │   ├── 📄 clusterworkflow_test.go
│   │   │   │   ├── 📄 clusterworkflow.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 clusterworkflowplane
│   │   │   │   ├── 📄 clusterworkflowplane.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 component
│   │   │   │   ├── 📄 component_test.go
│   │   │   │   ├── 📄 component.go
│   │   │   │   ├── 📄 logs_test.go
│   │   │   │   ├── 📄 logs.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   └── 📄 workflowrun_logs.go
│   │   │   ├── 📁 componentrelease
│   │   │   │   ├── 📄 componentrelease.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 resolver_test.go
│   │   │   │   └── 📄 resolver.go
│   │   │   ├── 📁 componenttype
│   │   │   │   ├── 📄 componenttype.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 config
│   │   │   │   ├── 📄 config_test.go
│   │   │   │   ├── 📄 config.go
│   │   │   │   ├── 📄 format_test.go
│   │   │   │   ├── 📄 format.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 storage_test.go
│   │   │   │   ├── 📄 storage.go
│   │   │   │   ├── 📄 stub.go
│   │   │   │   └── 📄 types.go
│   │   │   ├── 📁 dataplane
│   │   │   │   ├── 📄 dataplane.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 deploymentpipeline
│   │   │   │   ├── 📄 deploymentpipeline.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 environment
│   │   │   │   ├── 📄 environment.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 login
│   │   │   │   └── 📄 login.go
│   │   │   ├── 📁 logout
│   │   │   │   └── 📄 logout.go
│   │   │   ├── 📁 namespace
│   │   │   │   └── 📄 namespace.go
│   │   │   ├── 📁 observabilityalertsnotificationchannel
│   │   │   │   ├── 📄 observabilityalertsnotificationchannel.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 observabilityplane
│   │   │   │   ├── 📄 observabilityplane.go
│   │   │   │   └── 📄 params.go
│   │   │   ├── 📁 pagination
│   │   │   │   ├── 📄 pagination_test.go
│   │   │   │   └── 📄 pagination.go
│   │   │   ├── 📁 project
│   │   │   │   ├── 📄 params.go
│   │   │   │   └── 📄 project.go
│   │   │   ├── 📁 releasebinding
│   │   │   │   ├── 📄 derive_pipeline_test.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 releasebinding.go
│   │   │   │   ├── 📄 resolver_test.go
│   │   │   │   └── 📄 resolver.go
│   │   │   ├── 📁 secretreference
│   │   │   │   ├── 📄 params.go
│   │   │   │   └── 📄 secretreference.go
│   │   │   ├── 📁 setoverride
│   │   │   │   ├── 📄 setoverride_test.go
│   │   │   │   └── 📄 setoverride.go
│   │   │   ├── 📁 trait
│   │   │   │   ├── 📄 params.go
│   │   │   │   └── 📄 trait.go
│   │   │   ├── 📁 utils
│   │   │   │   ├── 📄 utils_test.go
│   │   │   │   └── 📄 utils.go
│   │   │   ├── 📁 workflow
│   │   │   │   ├── 📄 logs.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 workflow_test.go
│   │   │   │   └── 📄 workflow.go
│   │   │   ├── 📁 workflowplane
│   │   │   │   ├── 📄 params.go
│   │   │   │   └── 📄 workflowplane.go
│   │   │   ├── 📁 workflowrun
│   │   │   │   ├── 📄 logs_test.go
│   │   │   │   ├── 📄 logs.go
│   │   │   │   ├── 📄 params.go
│   │   │   │   ├── 📄 workflowrun_test.go
│   │   │   │   └── 📄 workflowrun.go
│   │   │   └── 📁 workload
│   │   │       ├── 📄 params.go
│   │   │       └── 📄 workload.go
│   │   ├── 📁 fsmode
│   │   │   ├── 📁 config
│   │   │   │   ├── 📄 release_config_test.go
│   │   │   │   └── 📄 release_config.go
│   │   │   ├── 📁 generator
│   │   │   │   ├── 📄 bulk_component_release_test.go
│   │   │   │   ├── 📄 bulk_component_release.go
│   │   │   │   ├── 📄 component_release_test.go
│   │   │   │   ├── 📄 component_release.go
│   │   │   │   ├── 📄 namer_test.go
│   │   │   │   ├── 📄 namer.go
│   │   │   │   ├── 📄 release_binding_test.go
│   │   │   │   └── 📄 release_binding.go
│   │   │   ├── 📁 output
│   │   │   │   ├── 📄 existing_test.go
│   │   │   │   ├── 📄 existing.go
│   │   │   │   ├── 📄 hash_test.go
│   │   │   │   ├── 📄 hash.go
│   │   │   │   ├── 📄 workload_writer_test.go
│   │   │   │   ├── 📄 workload_writer.go
│   │   │   │   ├── 📄 writer_test.go
│   │   │   │   └── 📄 writer.go
│   │   │   ├── 📁 pipeline
│   │   │   │   ├── 📄 pipeline_test.go
│   │   │   │   └── 📄 pipeline.go
│   │   │   ├── 📁 typed
│   │   │   │   ├── 📄 clustercomponenttype_test.go
│   │   │   │   ├── 📄 clustercomponenttype.go
│   │   │   │   ├── 📄 clustertrait_test.go
│   │   │   │   ├── 📄 clustertrait.go
│   │   │   │   ├── 📄 component_test.go
│   │   │   │   ├── 📄 component.go
│   │   │   │   ├── 📄 componenttype_test.go
│   │   │   │   ├── 📄 componenttype.go
│   │   │   │   ├── 📄 conversion_test.go
│   │   │   │   ├── 📄 conversion.go
│   │   │   │   ├── 📄 trait_test.go
│   │   │   │   ├── 📄 trait.go
│   │   │   │   ├── 📄 workload_test.go
│   │   │   │   └── 📄 workload.go
│   │   │   ├── 📄 gvk.go
│   │   │   ├── 📄 index_test.go
│   │   │   └── 📄 index.go
│   │   ├── 📁 resources
│   │   │   ├── 📁 client
│   │   │   │   ├── 📄 legacy_client.go
│   │   │   │   ├── 📄 obs_client.go
│   │   │   │   ├── 📄 openapi_client_test.go
│   │   │   │   └── 📄 openapi_client.go
│   │   │   ├── 📁 kinds
│   │   │   │   ├── 📄 component.go
│   │   │   │   ├── 📄 dataplane.go
│   │   │   │   ├── 📄 deploymentpipeline.go
│   │   │   │   ├── 📄 environment.go
│   │   │   │   ├── 📄 kindconstant.go
│   │   │   │   ├── 📄 namespace.go
│   │   │   │   ├── 📄 project.go
│   │   │   │   └── 📄 workload.go
│   │   │   ├── 📁 workload
│   │   │   │   ├── 📄 converter_test.go
│   │   │   │   └── 📄 converter.go
│   │   │   ├── 📄 base.go
│   │   │   ├── 📄 client.go
│   │   │   ├── 📄 format_test.go
│   │   │   ├── 📄 format.go
│   │   │   ├── 📄 options.go
│   │   │   ├── 📄 resource_base.go
│   │   │   ├── 📄 scheme.go
│   │   │   ├── 📄 status_test.go
│   │   │   ├── 📄 status.go
│   │   │   └── 📄 wrapper.go
│   │   ├── 📁 validation
│   │   │   ├── 📄 commands_test.go
│   │   │   ├── 📄 commands.go
│   │   │   ├── 📄 params_test.go
│   │   │   ├── 📄 params.go
│   │   │   ├── 📄 resources_test.go
│   │   │   ├── 📄 resources.go
│   │   │   ├── 📄 url_test.go
│   │   │   └── 📄 url.go
│   │   ├── 📄 impl.go
│   │   └── 📄 init.go
│   ├── 📁 openchoreo-api
│   │   ├── 📁 api
│   │   │   ├── 📁 gen
│   │   │   │   ├── 📄 client.gen.go
│   │   │   │   ├── 📄 models.gen.go
│   │   │   │   └── 📄 server.gen.go
│   │   │   ├── 📁 handlers
│   │   │   │   ├── 📄 authz.go
│   │   │   │   ├── 📄 cluster_scoped_handlers_test.go
│   │   │   │   ├── 📄 clustercomponenttypes.go
│   │   │   │   ├── 📄 clusterdataplanes.go
│   │   │   │   ├── 📄 clusterobservabilityplanes.go
│   │   │   │   ├── 📄 clustertraits.go
│   │   │   │   ├── 📄 clusterworkflowplanes.go
│   │   │   │   ├── 📄 clusterworkflows.go
│   │   │   │   ├── 📄 component_releases.go
│   │   │   │   ├── 📄 components_test.go
│   │   │   │   ├── 📄 components.go
│   │   │   │   ├── 📄 componenttypes.go
│   │   │   │   ├── 📄 convert_test.go
│   │   │   │   ├── 📄 convert.go
│   │   │   │   ├── 📄 dataplanes.go
│   │   │   │   ├── 📄 deployment_pipelines.go
│   │   │   │   ├── 📄 environments_test.go
│   │   │   │   ├── 📄 environments.go
│   │   │   │   ├── 📄 git_secrets.go
│   │   │   │   ├── 📄 handler.go
│   │   │   │   ├── 📄 namespaces.go
│   │   │   │   ├── 📄 oauth_metadata.go
│   │   │   │   ├── 📄 observability_alerts_notification_channels.go
│   │   │   │   ├── 📄 observabilityplanes.go
│   │   │   │   ├── 📄 operations.go
│   │   │   │   ├── 📄 pagination.go
│   │   │   │   ├── 📄 projects.go
│   │   │   │   ├── 📄 release_bindings.go
│   │   │   │   ├── 📄 releasebinding_k8sresources.go
│   │   │   │   ├── 📄 response.go
│   │   │   │   ├── 📄 secret_references.go
│   │   │   │   ├── 📄 traits.go
│   │   │   │   ├── 📄 webhook_handler_test.go
│   │   │   │   ├── 📄 webhook_handler.go
│   │   │   │   ├── 📄 workflowplanes.go
│   │   │   │   ├── 📄 workflows.go
│   │   │   │   └── 📄 workloads.go
│   │   │   ├── 📄 cfg-client.yaml
│   │   │   ├── 📄 cfg-models.yaml
│   │   │   └── 📄 cfg-server.yaml
│   │   ├── 📁 audit
│   │   │   └── 📄 definitions.go
│   │   ├── 📁 clients
│   │   │   └── 📄 k8s.go
│   │   ├── 📁 config
│   │   │   ├── 📄 cluster_gateway.go
│   │   │   ├── 📄 config.go
│   │   │   ├── 📄 env.go
│   │   │   ├── 📄 identity.go
│   │   │   ├── 📄 logging.go
│   │   │   ├── 📄 mcp_test.go
│   │   │   ├── 📄 mcp.go
│   │   │   ├── 📄 security_test.go
│   │   │   ├── 📄 security.go
│   │   │   ├── 📄 server_test.go
│   │   │   └── 📄 server.go
│   │   ├── 📁 mcphandlers
│   │   │   ├── 📄 cluster_resources.go
│   │   │   ├── 📄 components.go
│   │   │   ├── 📄 dataplanes.go
│   │   │   ├── 📄 environments.go
│   │   │   ├── 📄 handler.go
│   │   │   ├── 📄 helpers.go
│   │   │   ├── 📄 namespaces.go
│   │   │   ├── 📄 pe.go
│   │   │   ├── 📄 platform_standards.go
│   │   │   ├── 📄 projects.go
│   │   │   ├── 📄 transform_resources.go
│   │   │   ├── 📄 transform_test.go
│   │   │   └── 📄 transform.go
│   │   ├── 📁 models
│   │   │   ├── 📄 request_test.go
│   │   │   ├── 📄 request.go
│   │   │   └── 📄 response.go
│   │   └── 📁 services
│   │       ├── 📁 authz
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 autobuild
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_test.go
│   │       │   ├── 📄 service.go
│   │       │   ├── 📄 webhook_processor_test.go
│   │       │   └── 📄 webhook_processor.go
│   │       ├── 📁 clustercomponenttype
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 clusterdataplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 clusterobservabilityplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 clustertrait
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 clusterworkflow
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 clusterworkflowplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 component
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 componentrelease
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 componenttype
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 dataplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 deploymentpipeline
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 environment
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 git
│   │       │   ├── 📄 bitbucket.go
│   │       │   ├── 📄 github.go
│   │       │   ├── 📄 gitlab.go
│   │       │   └── 📄 provider.go
│   │       ├── 📁 gitsecret
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 handlerservices
│   │       │   └── 📄 services.go
│   │       ├── 📁 k8sresources
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 namespace
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 observabilityalertsnotificationchannel
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 observabilityplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 project
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 releasebinding
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 secretreference
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 testutil
│   │       │   └── 📄 testutil.go
│   │       ├── 📁 trait
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 workflow
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 workflowplane
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 workflowrun
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📁 workload
│   │       │   ├── 📄 errors.go
│   │       │   ├── 📄 interface.go
│   │       │   ├── 📄 service_authz.go
│   │       │   ├── 📄 service_test.go
│   │       │   └── 📄 service.go
│   │       ├── 📄 authz_test.go
│   │       ├── 📄 authz.go
│   │       ├── 📄 errors.go
│   │       ├── 📄 pagination_test.go
│   │       ├── 📄 pagination.go
│   │       └── 📄 utils.go
│   ├── 📁 patch
│   │   ├── 📄 expand_paths_test.go
│   │   ├── 📄 expand_paths.go
│   │   ├── 📄 fuzz_test.go
│   │   ├── 📄 helpers.go
│   │   ├── 📄 merge.go
│   │   ├── 📄 patch_test.go
│   │   ├── 📄 patch.go
│   │   ├── 📄 rfc6902.go
│   │   └── 📄 types.go
│   ├── 📁 pipeline
│   │   ├── 📁 component
│   │   │   ├── 📁 context
│   │   │   │   ├── 📄 builder_test.go
│   │   │   │   ├── 📄 cel_extensions_test.go
│   │   │   │   ├── 📄 cel_extensions.go
│   │   │   │   ├── 📄 cel_return_types.go
│   │   │   │   ├── 📄 component_test.go
│   │   │   │   ├── 📄 component.go
│   │   │   │   ├── 📄 configuration_test.go
│   │   │   │   ├── 📄 configuration.go
│   │   │   │   ├── 📄 embedded_trait_test.go
│   │   │   │   ├── 📄 embedded_trait.go
│   │   │   │   ├── 📄 trait_unit_test.go
│   │   │   │   ├── 📄 trait.go
│   │   │   │   ├── 📄 types.go
│   │   │   │   ├── 📄 workload_test.go
│   │   │   │   └── 📄 workload.go
│   │   │   ├── 📁 renderer
│   │   │   │   ├── 📄 controlflow_test.go
│   │   │   │   ├── 📄 controlflow.go
│   │   │   │   ├── 📄 foreach_test.go
│   │   │   │   ├── 📄 foreach.go
│   │   │   │   ├── 📄 renderer_test.go
│   │   │   │   └── 📄 renderer.go
│   │   │   ├── 📁 testdata
│   │   │   │   ├── 📁 configurations-and-secrets
│   │   │   │   │   ├── 📄 expected-resources-with-config-helpers.yaml
│   │   │   │   │   ├── 📄 expected-resources.yaml
│   │   │   │   │   ├── 📄 secret-references.yaml
│   │   │   │   │   ├── 📄 settings.yaml
│   │   │   │   │   ├── 📄 snapshot-with-config-helpers.yaml
│   │   │   │   │   └── 📄 snapshot.yaml
│   │   │   │   └── 📄 component-with-traits.yaml
│   │   │   ├── 📁 trait
│   │   │   │   ├── 📄 processor_test.go
│   │   │   │   └── 📄 processor.go
│   │   │   ├── 📄 benchmark_test.go
│   │   │   ├── 📄 pipeline_test.go
│   │   │   ├── 📄 pipeline.go
│   │   │   └── 📄 types.go
│   │   └── 📁 workflow
│   │       ├── 📄 pipeline_test.go
│   │       ├── 📄 pipeline.go
│   │       └── 📄 types.go
│   ├── 📁 scaffold
│   │   └── 📁 component
│   │       ├── 📁 testdata
│   │       │   ├── 📄 array_scaffolding_input.yaml
│   │       │   ├── 📄 array_scaffolding_want.yaml
│   │       │   ├── 📄 basic_types_input.yaml
│   │       │   ├── 📄 basic_types_want.yaml
│   │       │   ├── 📄 collection_shapes_input.yaml
│   │       │   ├── 📄 collection_shapes_want.yaml
│   │       │   ├── 📄 escaping_quoting_input.yaml
│   │       │   ├── 📄 escaping_quoting_want.yaml
│   │       │   ├── 📄 map_scaffolding_input.yaml
│   │       │   ├── 📄 map_scaffolding_want.yaml
│   │       │   ├── 📄 minimal_comments_false_input.yaml
│   │       │   ├── 📄 minimal_comments_false_want.yaml
│   │       │   ├── 📄 minimal_comments_true_input.yaml
│   │       │   ├── 📄 minimal_comments_true_want.yaml
│   │       │   ├── 📄 object_defaults_input.yaml
│   │       │   ├── 📄 object_defaults_want.yaml
│   │       │   ├── 📄 validation_and_types_input.yaml
│   │       │   ├── 📄 validation_and_types_want.yaml
│   │       │   ├── 📄 with_traits_input.yaml
│   │       │   ├── 📄 with_traits_want.yaml
│   │       │   ├── 📄 with_workflow_input.yaml
│   │       │   └── 📄 with_workflow_want.yaml
│   │       ├── 📄 field_context.go
│   │       ├── 📄 field_renderer_helpers.go
│   │       ├── 📄 field_renderer.go
│   │       ├── 📄 field_strategy.go
│   │       ├── 📄 generator_test.go
│   │       ├── 📄 generator.go
│   │       ├── 📄 nested_type_renderer.go
│   │       ├── 📄 rendering_helpers.go
│   │       ├── 📄 schema_analyzer.go
│   │       ├── 📄 schema_defaults.go
│   │       ├── 📄 strategy_array.go
│   │       ├── 📄 strategy_map.go
│   │       ├── 📄 strategy_object.go
│   │       ├── 📄 strategy_primitive.go
│   │       └── 📄 yaml_builder.go
│   ├── 📁 schema
│   │   ├── 📁 extractor
│   │   │   ├── 📄 schema_test.go
│   │   │   └── 📄 schema.go
│   │   ├── 📁 testdata
│   │   │   ├── 📄 invalid_circular_ref.yaml
│   │   │   ├── 📄 nested_openapiv3.yaml
│   │   │   ├── 📄 simple_openapiv3.yaml
│   │   │   └── 📄 with_refs_openapiv3.yaml
│   │   ├── 📄 definition_test.go
│   │   ├── 📄 definition.go
│   │   ├── 📄 openapiv3_test.go
│   │   ├── 📄 openapiv3.go
│   │   ├── 📄 ref_resolver_test.go
│   │   └── 📄 ref_resolver.go
│   ├── 📁 server
│   │   ├── 📁 middleware
│   │   │   ├── 📁 audit
│   │   │   │   ├── 📄 context.go
│   │   │   │   ├── 📄 logger.go
│   │   │   │   ├── 📄 middleware.go
│   │   │   │   ├── 📄 resolver.go
│   │   │   │   └── 📄 types.go
│   │   │   ├── 📁 auth
│   │   │   │   ├── 📁 jwt
│   │   │   │   │   ├── 📄 config_test.go
│   │   │   │   │   ├── 📄 config.go
│   │   │   │   │   ├── 📄 context.go
│   │   │   │   │   ├── 📄 errors.go
│   │   │   │   │   ├── 📄 extractor.go
│   │   │   │   │   ├── 📄 helpers.go
│   │   │   │   │   ├── 📄 jwks.go
│   │   │   │   │   ├── 📄 middleware_test.go
│   │   │   │   │   ├── 📄 middleware.go
│   │   │   │   │   ├── 📄 resolver_test.go
│   │   │   │   │   └── 📄 resolver.go
│   │   │   │   ├── 📁 subject
│   │   │   │   │   ├── 📄 config.go
│   │   │   │   │   └── 📄 resolver.go
│   │   │   │   ├── 📄 interface.go
│   │   │   │   └── 📄 openapi.go
│   │   │   ├── 📁 logger
│   │   │   │   ├── 📄 context.go
│   │   │   │   └── 📄 middleware.go
│   │   │   ├── 📁 mcp
│   │   │   │   ├── 📄 auth401_test.go
│   │   │   │   └── 📄 auth401.go
│   │   │   └── 📄 chain.go
│   │   ├── 📁 oauth
│   │   │   ├── 📄 metadata_test.go
│   │   │   └── 📄 metadata.go
│   │   └── 📄 server.go
│   ├── 📁 template
│   │   ├── 📄 cel_extensions_test.go
│   │   ├── 📄 custom_functions_test.go
│   │   ├── 📄 custom_functions.go
│   │   ├── 📄 engine_cache_test.go
│   │   ├── 📄 engine_cache.go
│   │   ├── 📄 engine_convert_test.go
│   │   ├── 📄 engine_test.go
│   │   └── 📄 engine.go
│   ├── 📁 validation
│   │   ├── 📁 component
│   │   │   ├── 📁 decltype
│   │   │   │   ├── 📄 extract.go
│   │   │   │   ├── 📄 reflect_test.go
│   │   │   │   └── 📄 reflect.go
│   │   │   ├── 📄 cel_env_test.go
│   │   │   ├── 📄 cel_env.go
│   │   │   ├── 📄 cel_validator_test.go
│   │   │   ├── 📄 cel_validator.go
│   │   │   ├── 📄 component_traits_test.go
│   │   │   ├── 📄 component_traits.go
│   │   │   ├── 📄 componenttype_test.go
│   │   │   ├── 📄 componenttype.go
│   │   │   ├── 📄 foreach_types.go
│   │   │   ├── 📄 resource_template.go
│   │   │   ├── 📄 trait_test.go
│   │   │   └── 📄 trait.go
│   │   └── 📁 schemautil
│   │       ├── 📄 extract_test.go
│   │       └── 📄 extract.go
│   ├── 📁 version
│   │   └── 📄 version.go
│   └── 📁 webhook
│       ├── 📁 clustercomponenttype
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 clustertrait
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 clusterworkflow
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 component
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 componentrelease
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 componenttype
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 project
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 releasebinding
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       ├── 📁 trait
│       │   ├── 📄 suite_test.go
│       │   ├── 📄 webhook_test.go
│       │   └── 📄 webhook.go
│       └── 📁 workflow
│           ├── 📄 suite_test.go
│           ├── 📄 webhook_test.go
│           └── 📄 webhook.go
├── 📁 logo
│   └── 📄 choreo-logo-black.svg
├── 📁 make
│   ├── 📄 common.mk
│   ├── 📄 docker.mk
│   ├── 📄 e2e.mk
│   ├── 📄 golang.mk
│   ├── 📄 helm.mk
│   ├── 📄 k3d.mk
│   ├── 📄 kube.mk
│   ├── 📄 lint.mk
│   └── 📄 tools.mk
├── 📁 openapi
│   ├── 📄 observer-api.yaml
│   └── 📄 openchoreo-api.yaml
├── 📁 pkg
│   ├── 📁 cli
│   │   ├── 📁 cmd
│   │   │   ├── 📁 apply
│   │   │   │   └── 📄 apply.go
│   │   │   ├── 📁 authzrole
│   │   │   │   └── 📄 authzrole.go
│   │   │   ├── 📁 authzrolebinding
│   │   │   │   └── 📄 authzrolebinding.go
│   │   │   ├── 📁 clusterauthzrole
│   │   │   │   └── 📄 clusterauthzrole.go
│   │   │   ├── 📁 clusterauthzrolebinding
│   │   │   │   └── 📄 clusterauthzrolebinding.go
│   │   │   ├── 📁 clustercomponenttype
│   │   │   │   ├── 📄 clustercomponenttype_test.go
│   │   │   │   └── 📄 clustercomponenttype.go
│   │   │   ├── 📁 clusterdataplane
│   │   │   │   └── 📄 clusterdataplane.go
│   │   │   ├── 📁 clusterobservabilityplane
│   │   │   │   └── 📄 clusterobservabilityplane.go
│   │   │   ├── 📁 clustertrait
│   │   │   │   ├── 📄 clustertrait_test.go
│   │   │   │   └── 📄 clustertrait.go
│   │   │   ├── 📁 clusterworkflow
│   │   │   │   ├── 📄 clusterworkflow_test.go
│   │   │   │   └── 📄 clusterworkflow.go
│   │   │   ├── 📁 clusterworkflowplane
│   │   │   │   └── 📄 clusterworkflowplane.go
│   │   │   ├── 📁 component
│   │   │   │   ├── 📄 component_test.go
│   │   │   │   └── 📄 component.go
│   │   │   ├── 📁 componentrelease
│   │   │   │   └── 📄 generate.go
│   │   │   ├── 📁 componenttype
│   │   │   │   └── 📄 componenttype.go
│   │   │   ├── 📁 config
│   │   │   │   └── 📄 config.go
│   │   │   ├── 📁 dataplane
│   │   │   │   └── 📄 dataplane.go
│   │   │   ├── 📁 deploymentpipeline
│   │   │   │   └── 📄 deploymentpipeline.go
│   │   │   ├── 📁 environment
│   │   │   │   └── 📄 environment.go
│   │   │   ├── 📁 login
│   │   │   │   └── 📄 login.go
│   │   │   ├── 📁 logout
│   │   │   │   └── 📄 logout.go
│   │   │   ├── 📁 namespace
│   │   │   │   └── 📄 namespace.go
│   │   │   ├── 📁 observabilityalertsnotificationchannel
│   │   │   │   └── 📄 observabilityalertsnotificationchannel.go
│   │   │   ├── 📁 observabilityplane
│   │   │   │   └── 📄 observabilityplane.go
│   │   │   ├── 📁 project
│   │   │   │   └── 📄 project.go
│   │   │   ├── 📁 releasebinding
│   │   │   │   └── 📄 generate.go
│   │   │   ├── 📁 secretreference
│   │   │   │   └── 📄 secretreference.go
│   │   │   ├── 📁 trait
│   │   │   │   └── 📄 trait.go
│   │   │   ├── 📁 version
│   │   │   │   └── 📄 version.go
│   │   │   ├── 📁 workflow
│   │   │   │   └── 📄 workflow.go
│   │   │   ├── 📁 workflowplane
│   │   │   │   └── 📄 workflowplane.go
│   │   │   ├── 📁 workflowrun
│   │   │   │   └── 📄 workflowrun.go
│   │   │   └── 📁 workload
│   │   │       └── 📄 workload.go
│   │   ├── 📁 common
│   │   │   ├── 📁 args
│   │   │   │   ├── 📄 args_test.go
│   │   │   │   └── 📄 args.go
│   │   │   ├── 📁 auth
│   │   │   │   └── 📄 auth.go
│   │   │   ├── 📁 builder
│   │   │   │   └── 📄 builder.go
│   │   │   ├── 📁 config
│   │   │   │   └── 📄 config.go
│   │   │   ├── 📁 constants
│   │   │   │   ├── 📄 crds.go
│   │   │   │   └── 📄 definitions.go
│   │   │   └── 📁 messages
│   │   │       └── 📄 messages.go
│   │   ├── 📁 core
│   │   │   └── 📁 root
│   │   │       └── 📄 root.go
│   │   ├── 📁 flags
│   │   │   └── 📄 flags.go
│   │   ├── 📁 types
│   │   │   └── 📁 api
│   │   │       ├── 📄 api.go
│   │   │       └── 📄 params.go
│   │   └── 📄 README.md
│   ├── 📁 fsindex
│   │   ├── 📁 cache
│   │   │   ├── 📄 benchmark_test.go
│   │   │   ├── 📄 cache_test.go
│   │   │   └── 📄 cache.go
│   │   ├── 📁 index
│   │   │   ├── 📄 index_test.go
│   │   │   ├── 📄 index.go
│   │   │   ├── 📄 serialize.go
│   │   │   ├── 📄 types_test.go
│   │   │   └── 📄 types.go
│   │   └── 📁 scanner
│   │       ├── 📄 filter_test.go
│   │       ├── 📄 filter.go
│   │       ├── 📄 parser_test.go
│   │       ├── 📄 parser.go
│   │       ├── 📄 scanner_test.go
│   │       └── 📄 scanner.go
│   ├── 📁 hash
│   │   └── 📄 hash.go
│   ├── 📁 mcp
│   │   ├── 📁 tools
│   │   │   ├── 📄 build_specs_test.go
│   │   │   ├── 📄 component_specs_test.go
│   │   │   ├── 📄 component.go
│   │   │   ├── 📄 crdschema_test.go
│   │   │   ├── 📄 crdschema.go
│   │   │   ├── 📄 deployment_specs_test.go
│   │   │   ├── 📄 helpers.go
│   │   │   ├── 📄 integration_test.go
│   │   │   ├── 📄 mock_test.go
│   │   │   ├── 📄 namespace_specs_test.go
│   │   │   ├── 📄 namespace.go
│   │   │   ├── 📄 pe_specs_test.go
│   │   │   ├── 📄 pe.go
│   │   │   ├── 📄 project_specs_test.go
│   │   │   ├── 📄 project.go
│   │   │   ├── 📄 register.go
│   │   │   ├── 📄 registration_test.go
│   │   │   ├── 📄 setup_test.go
│   │   │   ├── 📄 types.go
│   │   │   └── 📄 validation_test.go
│   │   └── 📄 server.go
│   └── 📁 observability
│       ├── 📄 logs.go
│       └── 📄 traces.go
├── 📁 rca-agent
│   ├── 📁 src
│   │   ├── 📁 agent
│   │   │   ├── 📁 middleware
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 logging.py
│   │   │   │   ├── 📄 output_transformer.py
│   │   │   │   └── 📄 tool_error_handler.py
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 agent.py
│   │   │   ├── 📄 stream_parser.py
│   │   │   └── 📄 tool_registry.py
│   │   ├── 📁 api
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 agent_routes.py
│   │   │   └── 📄 report_routes.py
│   │   ├── 📁 auth
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 authz_client.py
│   │   │   ├── 📄 authz_models.py
│   │   │   ├── 📄 bearer.py
│   │   │   ├── 📄 dependencies.py
│   │   │   ├── 📄 jwt.py
│   │   │   └── 📄 oauth_client.py
│   │   ├── 📁 clients
│   │   │   ├── 📁 backend
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 report_backend.py
│   │   │   │   └── 📄 sql_backend.py
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 llm.py
│   │   │   ├── 📄 mcp.py
│   │   │   └── 📄 openchoreo_api.py
│   │   ├── 📁 models
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 base.py
│   │   │   ├── 📄 chat_response.py
│   │   │   ├── 📄 rca_report.py
│   │   │   └── 📄 remediation_result.py
│   │   ├── 📁 templates
│   │   │   ├── 📁 api
│   │   │   │   └── 📄 rca_request.j2
│   │   │   ├── 📁 middleware
│   │   │   │   ├── 📄 logs.j2
│   │   │   │   ├── 📄 metrics.j2
│   │   │   │   ├── 📄 trace_spans.j2
│   │   │   │   └── 📄 traces.j2
│   │   │   └── 📁 prompts
│   │   │       ├── 📄 chat_agent_prompt.j2
│   │   │       ├── 📄 rca_agent_prompt.j2
│   │   │       └── 📄 remed_agent_prompt.j2
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py
│   │   ├── 📄 helpers.py
│   │   ├── 📄 logging_config.py
│   │   ├── 📄 main.py
│   │   └── 📄 template_manager.py
│   ├── 📄 .dockerignore
│   ├── 📄 .gitignore
│   ├── 📄 .python-version
│   ├── 📄 auth-config.yaml
│   ├── 📄 Dockerfile
│   ├── 📄 Makefile
│   ├── 📄 openapi.yaml
│   ├── 📄 pyproject.toml
│   ├── 📄 README.md
│   └── 📄 uv.lock
├── 📁 samples
│   ├── 📁 component-alerts
│   │   ├── 📄 alert-notification-channels.yaml
│   │   ├── 📄 alert-rule-trait.yaml
│   │   ├── 📄 components-with-alert-rules.yaml
│   │   ├── 📄 failure-scenario-setup.yaml
│   │   ├── 📄 README.md
│   │   └── 📄 trigger-alerts.sh
│   ├── 📁 component-types
│   │   ├── 📁 component-http-service
│   │   │   ├── 📄 http-service-component.yaml
│   │   │   └── 📄 README.md
│   │   ├── 📁 component-web-app
│   │   │   ├── 📄 README.md
│   │   │   └── 📄 webapp-component.yaml
│   │   ├── 📁 component-with-configs
│   │   │   ├── 📄 component-with-configs.yaml
│   │   │   └── 📄 README.md
│   │   └── 📁 component-with-embedded-traits
│   │       ├── 📄 component-with-embedded-traits.yaml
│   │       └── 📄 README.md
│   ├── 📁 from-image
│   │   ├── 📁 echo-websocket-service
│   │   │   ├── 📄 echo-websocket-service.yaml
│   │   │   └── 📄 README.md
│   │   ├── 📁 go-greeter-service
│   │   │   ├── 📄 greeter-service.yaml
│   │   │   └── 📄 README.md
│   │   ├── 📁 issue-reporter-schedule-task
│   │   │   ├── 📄 github-issue-reporter.yaml
│   │   │   └── 📄 README.md
│   │   └── 📁 react-starter-web-app
│   │       ├── 📄 react-starter.yaml
│   │       └── 📄 README.md
│   ├── 📁 from-source
│   │   ├── 📁 projects
│   │   │   └── 📁 url-shortener
│   │   │       ├── 📁 alerting-demo
│   │   │       │   ├── 📄 alert-notification-channels.yaml
│   │   │       │   ├── 📄 enable-alert.yaml
│   │   │       │   ├── 📄 failure-scenario.yaml
│   │   │       │   └── 📄 trigger-alerts.sh
│   │   │       ├── 📁 components
│   │   │       │   ├── 📄 analytics-service.yaml
│   │   │       │   ├── 📄 api-service.yaml
│   │   │       │   ├── 📄 frontend.yaml
│   │   │       │   ├── 📄 postgres.yaml
│   │   │       │   └── 📄 redis.yaml
│   │   │       ├── 📄 project.yaml
│   │   │       └── 📄 README.md
│   │   ├── 📁 services
│   │   │   ├── 📁 ballerina-buildpack-patient-management
│   │   │   │   ├── 📄 patient-management-service.yaml
│   │   │   │   └── 📄 README.md
│   │   │   ├── 📁 go-docker-greeter
│   │   │   │   ├── 📄 greeting-service.yaml
│   │   │   │   └── 📄 README.md
│   │   │   └── 📁 go-google-buildpack-reading-list
│   │   │       ├── 📄 reading-list-service.yaml
│   │   │       └── 📄 README.md
│   │   └── 📁 web-apps
│   │       └── 📁 react-starter
│   │           ├── 📄 react-web-app.yaml
│   │           └── 📄 README.md
│   ├── 📁 gcp-microservices-demo
│   │   ├── 📁 components
│   │   │   ├── 📄 ad-component.yaml
│   │   │   ├── 📄 cart-component.yaml
│   │   │   ├── 📄 checkout-component.yaml
│   │   │   ├── 📄 currency-component.yaml
│   │   │   ├── 📄 email-component.yaml
│   │   │   ├── 📄 frontend-component.yaml
│   │   │   ├── 📄 payment-component.yaml
│   │   │   ├── 📄 productcatalog-component.yaml
│   │   │   ├── 📄 recommendation-component.yaml
│   │   │   ├── 📄 redis-component.yaml
│   │   │   └── 📄 shipping-component.yaml
│   │   ├── 📄 gcp-microservice-demo-project.yaml
│   │   └── 📄 README.md
│   ├── 📁 getting-started
│   │   ├── 📁 ci-workflows
│   │   │   ├── 📄 ballerina-buildpack-builder.yaml
│   │   │   ├── 📄 dockerfile-builder.yaml
│   │   │   ├── 📄 gcp-buildpacks-builder.yaml
│   │   │   └── 📄 paketo-buildpacks-builder.yaml
│   │   ├── 📁 component-traits
│   │   │   └── 📄 alert-rule-trait.yaml
│   │   ├── 📁 component-types
│   │   │   ├── 📄 scheduled-task.yaml
│   │   │   ├── 📄 service.yaml
│   │   │   ├── 📄 webapp.yaml
│   │   │   └── 📄 worker.yaml
│   │   ├── 📁 workflow-templates
│   │   │   ├── 📄 ballerina-buildpack-build.yaml
│   │   │   ├── 📄 checkout-source.yaml
│   │   │   ├── 📄 containerfile-build.yaml
│   │   │   ├── 📄 gcp-buildpacks-build.yaml
│   │   │   ├── 📄 generate-workload-k3d.yaml
│   │   │   ├── 📄 generate-workload.yaml
│   │   │   ├── 📄 paketo-buildpacks-build.yaml
│   │   │   ├── 📄 publish-image-k3d.yaml
│   │   │   └── 📄 publish-image.yaml
│   │   ├── 📄 all.yaml
│   │   ├── 📄 deployment-pipeline.yaml
│   │   ├── 📄 environments.yaml
│   │   ├── 📄 project.yaml
│   │   ├── 📄 README.md
│   │   └── 📄 workflow-templates.yaml
│   ├── 📁 mcp
│   │   ├── 📁 build-failures
│   │   │   └── 📄 README.md
│   │   ├── 📁 configs
│   │   │   └── 📄 README.md
│   │   ├── 📁 getting-started
│   │   │   └── 📄 README.md
│   │   ├── 📁 log-analysis
│   │   │   └── 📄 README.md
│   │   ├── 📁 resource-optimization
│   │   │   └── 📄 README.md
│   │   ├── 📁 service-deployment
│   │   │   ├── 📁 developer-chat
│   │   │   │   └── 📄 README.md
│   │   │   ├── 📁 step-by-step
│   │   │   │   └── 📄 README.md
│   │   │   └── 📄 README.md
│   │   └── 📄 README.md
│   ├── 📁 occ-cli
│   │   └── 📁 go-greeter-manual-deploy
│   │       ├── 📄 greeter-service.yaml
│   │       └── 📄 README.md
│   ├── 📁 platform-config
│   │   ├── 📁 new-deployment-pipeline
│   │   │   ├── 📄 deployment-pipeline.yaml
│   │   │   └── 📄 README.md
│   │   └── 📁 new-environments
│   │       ├── 📄 development-environment.yaml
│   │       ├── 📄 pre-production-environment.yaml
│   │       ├── 📄 production-environment.yaml
│   │       ├── 📄 qa-environment.yaml
│   │       └── 📄 README.md
│   ├── 📁 workflows
│   │   ├── 📁 aws-rds-postgres
│   │   │   ├── 📁 terraform
│   │   │   │   ├── 📄 main.tf
│   │   │   │   ├── 📄 outputs.tf
│   │   │   │   └── 📄 variables.tf
│   │   │   ├── 📄 aws-rds-postgres-create.yaml
│   │   │   ├── 📄 aws-rds-postgres-delete.yaml
│   │   │   └── 📄 README.md
│   │   ├── 📁 github-stats-report
│   │   │   ├── 📄 cluster-workflow-template-github-stats-report.yaml
│   │   │   ├── 📄 README.md
│   │   │   ├── 📄 workflow-github-stats-report.yaml
│   │   │   └── 📄 workflow-run-github-stats-report.yaml
│   │   ├── 📁 scm-create-repo
│   │   │   ├── 📄 codecommit-create-repo.yaml
│   │   │   ├── 📄 github-create-repo.yaml
│   │   │   └── 📄 README.md
│   │   └── 📄 README.md
│   └── 📄 README.md
├── 📁 test
│   ├── 📁 e2e
│   │   ├── 📁 framework
│   │   │   ├── 📄 kubectl.go
│   │   │   └── 📄 wait.go
│   │   ├── 📁 k3d
│   │   │   ├── 📄 clusterdataplane.yaml
│   │   │   ├── 📄 config.yaml
│   │   │   ├── 📄 coredns-custom.yaml
│   │   │   ├── 📄 dataplane.yaml
│   │   │   ├── 📄 internal-gateway.yaml
│   │   │   ├── 📄 observabilityplane.yaml
│   │   │   ├── 📄 secretstore.yaml
│   │   │   ├── 📄 values-cp.yaml
│   │   │   ├── 📄 values-dp.yaml
│   │   │   ├── 📄 values-op.yaml
│   │   │   ├── 📄 values-thunder.yaml
│   │   │   ├── 📄 values-wp.yaml
│   │   │   └── 📄 workflowplane.yaml
│   │   ├── 📁 suites
│   │   │   ├── 📁 connections
│   │   │   │   ├── 📄 connections_fixtures_test.go
│   │   │   │   ├── 📄 connections_test.go
│   │   │   │   └── 📄 suite_test.go
│   │   │   └── 📁 networkpolicy
│   │   │       ├── 📄 networkpolicy_fixtures_test.go
│   │   │       ├── 📄 networkpolicy_test.go
│   │   │       └── 📄 suite_test.go
│   │   ├── 📄 e2e_suite_test.go
│   │   └── 📄 e2e_test.go
│   └── 📁 utils
│       └── 📄 utils.go
├── 📁 tools
│   ├── 📁 helm-gen
│   │   ├── 📄 crd.go
│   │   ├── 📄 generator.go
│   │   ├── 📄 main.go
│   │   ├── 📄 rbac.go
│   │   ├── 📄 README.md
│   │   └── 📄 webhook.go
│   └── 📁 licenser
│       ├── 📄 go.mod
│       ├── 📄 go.sum
│       ├── 📄 main_test.go
│       └── 📄 main.go
├── 📄 .coderabbit.yaml
├── 📄 .dockerignore
├── 📄 .gitignore
├── 📄 .golangci.yml
├── 📄 ADOPTERS.md
├── 📄 CHANGELOG.md
├── 📄 check-tools.sh
├── 📄 CODE_OF_CONDUCT.md
├── 📄 Dockerfile
├── 📄 go.mod
├── 📄 go.sum
├── 📄 GOVERNANCE.md
├── 📄 LICENSE
├── 📄 MAINTAINERS.md
├── 📄 Makefile
├── 📄 PROJECT
├── 📄 README.md
├── 📄 SECURITY.md
├── 📄 test-alerts-incidents.md
└── 📄 VERSION

File Contents:
---

File: docs/configure-controlplane-mcp-server.md
---
# Openchoreo MCP Server Configuration

> **DEPRECATED:** This document describes the legacy MCP server (`pkg/mcp/legacytools/`). The toolset code has been moved to `pkg/mcp/legacytools/` and the config key renamed from `mcp` to `legacy_mcp`. A new MCP server implementation is being developed.

This guide explains the OpenChoreo MCP (Model Context Protocol) server concepts, implementation and configuration.

## Architecture Overview

The MCP server implementation consists of three main components:

1. **Toolsets & Registration** (`pkg/mcp/tools.go`) - Defines tool handler interfaces organized by toolsets and registers them with the MCP server
2. **Server Setup** (`pkg/mcp/server.go`) - Creates HTTP and STDIO server instances
3. **Handler Implementation** (`internal/openchoreo-api/mcphandlers/`) - Implements the actual business logic

## Toolset Concept

Tools are organized into **Toolsets** - logical groupings of related functionality. Each toolset has its own handler interface.

**Available Toolsets:**
- `ToolsetNamespace` (`namespace`) - Namespace operations (get namespace details)
- `ToolsetProject` (`project`) - Project operations (list, get, create projects)
- `ToolsetComponent` (`component`) - Component operations (list, get, create components, bindings, workloads, releases, release bindings, deployment, promotion)
- `ToolsetBuild` (`build`) - Build operations (trigger builds, list builds, build templates, workflow planes)
- `ToolsetDeployment` (`deployment`) - Deployment operations (deployment pipelines, observer URLs)
- `ToolsetInfrastructure` (`infrastructure`) - Infrastructure operations (environments, data planes, component types, workflows, traits)
- `ToolsetSchema` (`schema`) - Schema operations (describe a given kind)
- `ToolsetResource` (`resource`) - Resource operations (kubectl-like apply/delete for OpenChoreo resources)

## Configuring Enabled Toolsets

Toolsets can be configured via the `MCP_TOOLSETS` environment variable. This allows you to enable/disable toolsets without code changes.

### Configuration

Set the `MCP_TOOLSETS` environment variable to a comma-separated list of toolsets:

```bash
# Enable only namespace and project toolsets
export MCP_TOOLSETS="namespace,project"

# Enable all toolsets (default)
export MCP_TOOLSETS="namespace,project,component,build,deployment,infrastructure,schema,resource"

# Enable specific toolsets for your use case
export MCP_TOOLSETS="namespace,project,component"
```

### Default Behavior

If `MCP_TOOLSETS` is not set, the system defaults to enabling all toolsets:
- `namespace`
- `project`
- `component`
- `build`
- `deployment`
- `infrastructure`
- `schema`
- `resource`

### Kubernetes/Helm Configuration

In production deployments, configure toolsets via Helm values:

```yaml
openchoreoApi:
  mcp:
    # Enable all toolsets (default)
    toolsets: "namespace,project,component,build,deployment,infrastructure,schema,resource"
    
    # Or enable specific toolsets based on your requirements
    # toolsets: "namespace,project,component"
```



File: docs/contributors/README.md
---
# Contributing to OpenChoreo

Welcome! We're excited that you're interested in contributing to OpenChoreo. Whether you're fixing a bug, improving documentation, or proposing new features, every contribution makes a difference.

## Getting Started

Before you start contributing, check out our guidelines:

- **[Contribution Guide](./contribute.md)** – Learn how to setup the development environment, make changes, and submit pull requests.
- **[GitHub Workflow](./github_workflow.md)** – Understand our GitHub workflow for submitting pull requests.
- **[Release Guide](./release.md)** – Guide to releasing a new version of OpenChoreo.
- **[Resource Kind Reference Guide](./../resource-kind-reference-guide.md)** – Get details about resource kinds in OpenChoreo.

## Need Help?

If you have any questions, join our **[Slack Community](https://cloud-native.slack.com/archives/C0ABYRG1MND)** or open a **[GitHub Discussion](https://github.com/openchoreo/openchoreo/discussions)**.

We appreciate your contributions—thank you for making OpenChoreo better! 



File: docs/contributors/adding-new-crd.md
---

# Adding New CRD Resources

This guide explains how to add new Custom Resource Definitions (CRDs) to the project using **Kubebuilder** and how to refactor the generated controller into a dedicated package for better project organization.

## Steps to Add a New CRD Resource

### 1. **Generate the CRD with Kubebuilder**

Run the following command to scaffold a new API group, version, and kind:
```bash
kubebuilder create api --group <group_name> --version <version> --kind <kind_name>
```

Replace `<version>`, and `<kind_name>` with the appropriate values for your resource. For example:
```bash
kubebuilder create api --version v1alpha1 --kind Component
```

> [!NOTE]
> The group name is not specified in the command because we use the empty group with domain `openchoreo.dev` configured in the PROJECT file.

This generates:
- **API types** under `api/<version>/`
- **Controller files** under `internal/controller/`:
    - `<kind_name>_controller.go`
    - `<kind_name>_controller_test.go`
    - `suite_test.go`

### 2. **Edit the API Types**

Modify the API types in `api/<version>/<kind_name>_types.go` as needed. Define your resource's fields and annotations.

### 3. **Run Code Generators**

Run the following command to generate code for deep copies, CRD manifests, and other boilerplate:

```bash
make generate
make manifests
```

### 4. **Register the New Controller**

By default, the generated controller is already registered in `main.go`. You’ll refactor this registration in the next steps.

---

## Steps to Refactor the Controller

### 1. **Move the Controller Files**

Manually move the generated controller and test files to a dedicated package under `internal/controller/<kind_name>/`.
Change the name of the controller file from `<kind_name>_controller.go` to `controller.go`.

For example:
```plaintext
internal/controller/
├── component/
│   ├── controller.go
│   ├── controller_test.go
│   └── suite_test.go
```

### 2. **Update Package Declarations**

Update the package declaration at the top of the moved files. Change it to match the new location. For example:
```go
package component
```

### 3. **Update Struct Name**

Update the struct name from `<Kind>Reconciler` to `Reconciler` in controller file. For example:

```go
type Reconciler struct {
    // Add fields here
}
```

### 4. **Update `suite_test.go`**

The `suite_test.go` file contains the setup of test environments which requires CRDs and Kubernetes binaries path.
The relative paths of this file need to be updated to reflect the new location of the controller.

Update the relative paths to account for the new location under `internal/controller/<kind>/`:

```go
By("bootstrapping test environment")
testEnv = &envtest.Environment{
    CRDDirectoryPaths:     []string{filepath.Join("..", "..", "..", "config", "crd", "bases")},
    ErrorIfCRDPathMissing: true,

    // The BinaryAssetsDirectory is only required if you want to run the tests directly
    // without call the makefile target test. If not informed it will look for the
    // default path defined in controller-runtime which is /usr/local/kubebuilder/.
    // Note that you must have the required binaries setup under the bin directory to perform
    // the tests directly. When we run make test it will be setup and used automatically.
    BinaryAssetsDirectory: filepath.Join("..", "..", "..", "bin", "tools", "k8s",
        fmt.Sprintf("1.32.0-%s-%s", runtime.GOOS, runtime.GOARCH)),
}
```

### 5. **Update Imports in `main.go`**

In `main.go`, update the import path for the moved controller and ensure it’s registered with the manager. For example:
```go
import (
	component "github.com/openchoreo/openchoreo/internal/controller/component"
)

// Register the controller
if err := (&component.Reconciler{
	Client: mgr.GetClient(),
    Scheme: mgr.GetScheme(),
}).SetupWithManager(mgr); err != nil {
	setupLog.Error(err, "unable to create controller", "controller", "Component")
	os.Exit(1)
}
```

### 4. **Test the Refactored Controller**

Run the following to verify that your changes are working as expected:

```bash
make test
```

## Update the helm chart 

Run the following to update the helm chart for your generated CRD.

```bash
make helm-generate
```



File: docs/contributors/adding-new-mcp-tools.md
---
# Adding New MCP Tools

> **DEPRECATED:** This document describes the legacy MCP server (`pkg/mcp/legacytools/`). The toolset code has been moved from `pkg/mcp/tools/` to `pkg/mcp/legacytools/`. A new MCP server implementation is being developed.

This guide explains how to add new tools to the OpenChoreo MCP server.

## Adding a New Tool

### Option A: Add to Existing Toolset

Follow these steps to add a tool to an existing toolset (e.g., ComponentToolset):

#### 1. Update the Toolset Handler Interface

In `pkg/mcp/tools.go`, add your method to the appropriate handler interface:

```go
type ComponentToolsetHandler interface {
    CreateComponent(ctx context.Context, namespaceName, projectName string, req *models.CreateComponentRequest) (string, error)
    YourNewMethod(ctx context.Context, param1 string, param2 int) (string, error)  // Add here
}
```

**Conventions:**
- Methods should return `(string, error)` - the string contains JSON-serialized response
- Keep method names descriptive and follow Go naming conventions
- First parameter should be `ctx context.Context`

#### 2. Register the Tool

In the `Register` method of `pkg/mcp/tools.go`, create a new registration function:

```go
func (t *Toolsets) RegisterYourNewTool(s *mcp.Server) {
    mcp.AddTool(s, &mcp.Tool{
        Name:        "your_tool_name",
        Description: "Clear description of what the tool does",
        InputSchema: createSchema(map[string]any{
            "param1": stringProperty("Description of param1"),
            "param2": numberProperty("Description of param2"),
        }, []string{"param1"}), // List required fields
    }, func(ctx context.Context, req *mcp.CallToolRequest, args struct {
        Param1 string `json:"param1"`
        Param2 int    `json:"param2"`
    }) (*mcp.CallToolResult, map[string]string, error) {
        result, err := t.ComponentToolset.YourNewMethod(ctx, args.Param1, args.Param2)
        return handleToolResult(result, err)
    })
}
```

Then add it to the appropriate toolset registration list (e.g., `componentToolRegistrations`):

```go
func (t *Toolsets) componentToolRegistrations() []RegisterFunc {
    return []RegisterFunc{
        t.RegisterListComponents,
        t.RegisterGetComponent,
        t.RegisterYourNewTool,  // Add here
    }
}
```

**Key Points:**
- Tool name should be lowercase with underscores (snake_case)
- Always check if the handler is nil before adding tools
- The args struct must have JSON tags matching the schema property names
- Always marshal the result as JSON
- Use `handleToolResult` helper function for consistent error handling

#### 3. Implement the Handler

In `internal/openchoreo-api/mcphandlers/`, implement your handler method in the appropriate file:

```go
func (h *MCPHandler) YourNewMethod(param1 string, param2 int) (string, error) {
    ctx := context.Background()
    
    // Call your service layer
    res, err := h.Services.YourService.DoSomething(ctx, param1, param2)
    if err != nil {
        return "", err
    }
    
    // Marshal to JSON string
    data, err := json.Marshal(res)
    if err != nil {
        return "", err
    }
    
    return string(data), nil
}
```

### Option B: Create a New Toolset

If you're adding a new category of tools, create a new toolset:

#### 1. Define the Toolset Type

In `pkg/mcp/tools.go`, add a new constant:

```go
const (
    ToolsetNamespace      ToolsetType = "namespace"
    ToolsetProject        ToolsetType = "project"
    ToolsetComponent      ToolsetType = "component"
    ToolsetBuild          ToolsetType = "build"
    ToolsetDeployment     ToolsetType = "deployment"
    ToolsetInfrastructure ToolsetType = "infrastructure"
    ToolsetYourNew        ToolsetType = "yournew"  // Add your toolset
)
```

#### 2. Create Handler Interface

Define a new handler interface:

```go
type YourNewToolsetHandler interface {
    Method1(ctx context.Context, param string) (string, error)
    Method2(ctx context.Context, id int) (string, error)
}
```

#### 3. Add to Toolsets Struct

```go
type Toolsets struct {
    NamespaceToolset      NamespaceToolsetHandler
    ProjectToolset        ProjectToolsetHandler
    ComponentToolset      ComponentToolsetHandler
    BuildToolset          BuildToolsetHandler
    DeploymentToolset     DeploymentToolsetHandler
    InfrastructureToolset InfrastructureToolsetHandler
    YourNewToolset        YourNewToolsetHandler  // Add your toolset
}
```

#### 4. Register Tools

Create registration functions and add them to a new toolset registration list:

```go
func (t *Toolsets) RegisterMethod1(s *mcp.Server) {
    mcp.AddTool(s, &mcp.Tool{
        Name:        "method1",
        Description: "Description",
        InputSchema: createSchema(map[string]any{
            "param": stringProperty("Parameter description"),
        }, []string{"param"}),
    }, func(ctx context.Context, req *mcp.CallToolRequest, args struct {
        Param string `json:"param"`
    }) (*mcp.CallToolResult, map[string]string, error) {
        result, err := t.YourNewToolset.Method1(ctx, args.Param)
        return handleToolResult(result, err)
    })
}

// Add more registration functions...

// Create a registration list function
func (t *Toolsets) yourNewToolRegistrations() []RegisterFunc {
    return []RegisterFunc{
        t.RegisterMethod1,
        // Add more tools...
    }
}
```

Then in the `Register` method, add your toolset registration:

```go
func (t *Toolsets) Register(s *mcp.Server) {
    // ... existing toolsets ...
    
    if t.YourNewToolset != nil {
        for _, registerFunc := range t.yourNewToolRegistrations() {
            registerFunc(s)
        }
    }
}
```

#### 5. Create Handler File

Create a new file in `internal/openchoreo-api/mcphandlers/` (e.g., `yournew.go`):

```go
package mcphandlers

import (
    "context"
    "encoding/json"
)

func (h *MCPHandler) Method1(ctx context.Context, param string) (string, error) {
    // Implementation
    res, err := h.Services.YourService.Method1(ctx, param)
    if err != nil {
        return "", err
    }
    
    data, err := json.Marshal(res)
    if err != nil {
        return "", err
    }
    
    return string(data), nil
}
```

#### 6. Update Toolset Initialization

Add your new toolset to the initialization logic in `internal/openchoreo-api/handlers/handlers.go`:

```go
func getMCPServerToolsets(h *Handler) *mcp.Toolsets {
    // ... existing code ...
    
    for toolsetType := range toolsetsMap {
        switch toolsetType {
        case mcp.ToolsetNamespace:
            toolsets.NamespaceToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetProject:
            toolsets.ProjectToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetComponent:
            toolsets.ComponentToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetBuild:
            toolsets.BuildToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetDeployment:
            toolsets.DeploymentToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetInfrastructure:
            toolsets.InfrastructureToolset = &mcphandlers.MCPHandler{Services: h.services}
        case mcp.ToolsetYourNew:  // Add your new toolset
            toolsets.YourNewToolset = &mcphandlers.MCPHandler{Services: h.services}
        default:
            h.logger.Warn("Unknown toolset type", slog.String("toolset", string(toolsetType)))
        }
    }
    return toolsets
}
```

Now users can enable your toolset by setting:
```bash
export MCP_TOOLSETS="namespace,project,yournew"
```

## Schema Helper Functions

Available helper functions for defining input schemas:

### `stringProperty(description string)`
Creates a string property:
```go
"name": stringProperty("User's name")
```

### `numberProperty(description string)`
Creates a number property:
```go
"age": numberProperty("User's age")
```

### `booleanProperty(description string)`
Creates a boolean property:
```go
"enabled": booleanProperty("Whether the feature is enabled")
```

### `arrayProperty(description string, itemType string)`
Creates an array property:
```go
"tags": arrayProperty("List of tags", "string")
```

### `enumProperty(description string, values []string)`
Creates an enum property with fixed allowed values:
```go
"format": enumProperty("Output format", []string{"json", "table", "yaml"})
```

### `createSchema(properties map[string]any, required []string)`
Creates the complete input schema:
```go
InputSchema: createSchema(map[string]any{
    "name": stringProperty("Required name parameter"),
    "age":  numberProperty("Optional age parameter"),
}, []string{"name"}) // Only "name" is required
```

**Note:** Some helper functions may be marked as unused by linters if they're not currently used in the codebase. This is expected for functions provided for future extensibility.

## Data Type Conventions

### Return Types
All handler methods **must** return `(string, error)`:
- The string should contain JSON-serialized data
- Use `json.Marshal()` to serialize responses
- Return empty string and error on failure

### Input Parameters
- Keep parameters simple (string, int, bool, etc.)
- Complex inputs should use structs with JSON tags
- JSON tags must match schema property names exactly

### Schema Types
- `string` - text values
- `number` / `integer` - numeric values
- `boolean` - true/false values
- `object` - nested structures
- `array` - lists of values

### Enums
Use `enumProperty()` for parameters with a fixed set of allowed values.



File: docs/contributors/build-engines.md
---
# OpenChoreo Build Engines

This document describes the pluggable build engine architecture in OpenChoreo and provides a practical, high-level guide for adding new build engines.

## Overview

OpenChoreo supports multiple build engines through a pluggable architecture that allows platform teams to choose the best build technology for their needs. The system currently supports:

- Argo Workflows (default) — Kubernetes-native workflow engine
- Tekton (planned) — Cloud-native CI/CD building blocks
- Custom Engines — Your own build implementation

## Architecture

### High-Level Architecture

```
Control Plane                                  Workflow Plane
┌───────────────────────────────────────┐      ┌─────────────────────────────┐
│                                       │      │                             │
│  ┌──────────────────┐                 │      │  Engine-Specific Resources: │
│  │ Build Controller │                 │      │  • Namespaces               │
│  │ - Watches Build  │                 │      │  • RBAC (SA, Role, RB)      │
│  │ - Status updates │                 │      │  • Workflows/Pipelines      │
│  │ - Conditions     │                 │      │  • Templates                │
│  └─────────┬────────┘                 │      │                             │
│            │                          │      └─────────────────────────────┘
│            │ delegates                │                     ▲
│            ▼                          │                     │
│  ┌─────────────────────────────────┐  │                     │
│  │ Builder (Mediator)              │  │                     │
│  │ ┌─────────────────────────────┐ │  │                     │
│  │ │ Engine Registry             │ │  │                     │
│  │ │ ┌─────────────────────────┐ │ │  │                     │
│  │ │ │ "argo" → ArgoEngine     │ │ │  │                     │
│  │ │ │         (implemented)   │ │ │  │                     │
│  │ │ │ "tekton" → TektonEngine │ │ │  │                     │
│  │ │ │           (planned)     │ │ │  │                     │
│  │ │ │ "custom" → YourEngine   │ │ │  │                     │
│  │ │ └─────────────────────────┘ │ │  │                     │
│  │ └─────────────────────────────┘ │  │                     │
│  │                                 │  │                     │
│  │ Engine Selection:               │  │                     │
│  │ • spec.templateRef.engine       │  │                     │
│  │ • Default: "argo"               │  │                     │
│  └─────────────────────────────────┘  │                     │
│                                       │                     │
└───────────────────────────────────────┘                     │
                                                              │
                             ┌────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ All Engines Implement Same Interface:                       │
│                                                             │
│ GetName() string                                            │
│ EnsurePrerequisites(ctx, wpClient, build) error             │
│ CreateBuild(ctx, wpClient, build) (response, error)         │
│ GetBuildStatus(ctx, wpClient, build) (status, error)        │
│ ExtractBuildArtifacts(ctx, wpClient, build) (artifacts, e)  │
└─────────────────────────────────────────────────────────────┘


Shared Utilities (Used by All Engines):
┌─────────────────────────────────────────────────────────────────────────────────┐
│ names package                          engines package                          │
│ ┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐ │
│ │ • MakeImageName(build)              │ │ • EnsureResource(ctx, client, obj)   │ │
│ │ • MakeWorkflowName(build)           │ │ • MakeNamespace(build)               │ │
│ │ • MakeNamespaceName(build)          │ │ • Standard step names                │ │
│ │ • MakeWorkflowLabels(build)         │ │                                      │ │
│ └─────────────────────────────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘

Build Lifecycle Flow:
1. Build CR created/updated
2. Controller calls Builder.ProcessBuild()
3. Builder selects engine based on spec.templateRef.engine
4. Builder gets workflow-plane client (cross-cluster)
5. Engine.EnsurePrerequisites() → Create namespace, RBAC, etc.
6. Engine.CreateBuild() → Create Workflow/PipelineRun/etc.
7. Controller periodically calls Engine.GetBuildStatus()
8. On success, Engine.ExtractBuildArtifacts() → Get image, workload CR
9. Builder updates Build status and creates Workload resource
```

### Component Structure

```
internal/controller/build/
├── builder.go                    # Builder mediator pattern (engine selection, lifecycle)
├── controller.go                 # Main build controller
├── controller_conditions.go      # Status condition management
├── engines/                      # Engine abstraction layer
│   ├── interface.go              # BuildEngine interface and shared types/utilities
│   └── argo/                     # Argo Workflows implementation (reference)
│       ├── engine.go             # Core Argo engine logic
│       └── workflow.go           # Argo workflow creation
├── names/                        # Naming utilities (used by engines)
│   ├── images.go                 # Docker image naming
│   ├── workflows.go              # Workflow/namespace naming
│   └── resources.go              # Kubernetes resource naming
```

## Engine Contract (What you must implement)

Every build engine must implement the following contract. The Builder calls these in order during the Build lifecycle. You do not need to change the controller or Builder to integrate a new engine, but you must register it (see "Register your engine").

- `GetName()`: Return a short unique identifier for the engine (e.g., "argo", "tekton").
- `EnsurePrerequisites(ctx, k8sClient, build)`: Create or verify any resources required to run builds. Typical items: namespace, service account, role, role binding, CRDs of the target engine, and any config maps/secrets. Must be idempotent.
- `CreateBuild(ctx, k8sClient, build)`: Start the build in the target engine (e.g., Workflow, PipelineRun). Must be idempotent and return an identifier and whether a new run was created.
- `GetBuildStatus(ctx, k8sClient, build)`: Return a normalized status with phase and message. Map engine-native phases to: Running, Succeeded, Failed, or Unknown.
- `ExtractBuildArtifacts(ctx, k8sClient, build)`: When the build is complete, extract artifacts such as the built image reference and the generated Workload custom resource (YAML string) from the engine’s outputs.

Shared types used across engines:
- `BuildCreationResponse`: `{ id, created }`
- `BuildStatus`: `{ phase, message }`
- `BuildArtifacts`: `{ image, workloadCR }`

## Engine Lifecycle in OpenChoreo

1. **Engine selection**
   - Builder determines the engine using `Build.spec.templateRef.engine`. If omitted, the default is `argo`.
2. **Prerequisites**
   - Builder calls `EnsurePrerequisites` to prepare namespace, RBAC, and engine-specific resources.
3. **Create or get build**
   - Builder calls `CreateBuild`. If the engine reports “already exists,” Builder treats it as a previously created run.
4. **Status tracking**
   - Builder periodically calls `GetBuildStatus` and updates `Build.status` conditions (`InProgress`, `Completed`, `Failed`).
5. **Artifact extraction**
   - When `Succeeded`, Builder calls `ExtractBuildArtifacts` and persists the image in `Build.status.imageStatus.image`.
6. **Workload creation** (optional, handled by Builder)
   - If a workload CR is present in artifacts, Builder creates the Workload resource in the Build’s namespace.

## Control Plane vs Workflow Plane

- The Builder runs in the control plane and talks to the workflow plane cluster selected by the WorkflowPlane resource.
- All engine methods (`EnsurePrerequisites`, `CreateBuild`, `GetBuildStatus`, `ExtractBuildArtifacts`) receive a Kubernetes client that targets the workflow plane. Do not assume access to control-plane resources inside the engine.
- Ensure that any CRDs and templates your engine needs are installed in the workflow plane cluster referenced by the WorkflowPlane.

## Artifact Contract (Outputs your engine should provide)

Engines should expose at least these outputs when the build succeeds:
- **Container image**: A fully qualified image reference (e.g., `registry.example.com/org/project:tag`).
- **Workload CR**: A serialized YAML string of a valid openchoreo Workload resource (optional, only if your template generates it).

Standard output names and steps:
- Prefer emitting an output parameter named `image` for the built image reference.
- Prefer emitting an output parameter named `workload-cr` containing the YAML string for the Workload resource.
- When modeling steps, use stable step/template names such as `publish-image` and `generate-workload-cr` for clarity and consistency across engines.

Argo reference implementation exposes these as named outputs that the Builder knows how to read. If you implement a new engine, ensure you can surface equivalent outputs and map them to the generic `BuildArtifacts` fields above. The Builder will then set `status.imageStatus.image` and create the Workload if `workload-cr` is present.

## Engine Selection and Configuration

- **Per-Build selection**: Users choose the engine in the Build resource under `spec.templateRef.engine` (e.g., "argo", "tekton").
- **Default engine**: If not set, the Builder defaults to `argo`. Platform teams can change this behavior in the Builder’s selection logic if needed.

Example Build snippet:

```yaml
spec:
  templateRef:
    name: docker-build
    engine: argo   # or tekton, or your engine name
    parameters:
      - name: dockerfile-path
        value: ./Dockerfile
```

## Adding a New Build Engine

Follow this checklist to add a new engine implementation:

1. **Create a new engine package**
   - Location: `internal/controller/build/engines/<your-engine>/`
   - Use the Argo engine as a structural reference only; do not copy logic blindly.

2. **Implement the engine contract**
   - Provide `GetName`, `EnsurePrerequisites`, `CreateBuild`, `GetBuildStatus`, and `ExtractBuildArtifacts`.
   - Ensure `EnsurePrerequisites` and `CreateBuild` are idempotent (safe to call multiple times).
   - Map your engine’s phases to the generic `BuildPhase` values.
   - Provide artifacts (image, workloadCR) in `ExtractBuildArtifacts` after success.

3. **Register your engine with the Builder**
   - Update `internal/controller/build/builder.go` in the `registerBuildEngines()` function to instantiate and store your engine by `GetName()`.
   - Ensure the name returned by `GetName()` matches the user-facing value in `Build.spec.templateRef.engine`.

4. **Use shared naming and labels**
   - Use the names package to construct workflow/pipeline names, namespaces, labels, and image names/tags.
   - Keep naming deterministic and collision-free.

5. **Template and resource expectations**
   - If your engine uses cluster templates (e.g., pipeline templates), ensure they are installed in the workflow plane cluster.
   - Ensure any engine CRDs are present.

6. **Security and RBAC**
   - Create a least-privileged ServiceAccount, Role, and RoleBinding in the build namespace.
   - Scope permissions to the engine’s required resources only.

7. **Status and observability**
   - Provide meaningful status messages for easier troubleshooting.
   - Expose engine-native IDs in logs to correlate with external systems.

8. **Testing**
   - Unit test your engine logic.
   - Use integration tests against a real API server (envtest or a local Kubernetes cluster like k3d).
   - Validate artifact extraction and workload creation end-to-end.

## Conventions and Shared Utilities

To ensure consistency across engines:

- **Naming utilities (names package)**
  - Image naming and tagging (e.g., `project-component:default`) based on Build metadata.
  - Workflow/pipeline and namespace naming helpers.
  - Standard labels for workflows/pipelines and related resources.

- **Prerequisite helpers (engines package)**
  - Use shared helpers to create namespaces and to apply resources idempotently.

- **Step names and outputs**
  - If your engine models steps, prefer consistent names, such as `publish-image` for the image push and `generate-workload-cr` for creating the Workload CR.
  - Expose outputs with stable names so `ExtractBuildArtifacts` can retrieve the image and workload CR reliably (`image`, `workload-cr`).

- **Ownership and cleanup**
  - Set owner references where appropriate so that resources are garbage-collected when a Build is deleted.

## Best Practices

- **What the Builder does (do not duplicate in engines)**
  - Chooses the engine and invokes its lifecycle methods.
  - Updates `status.conditions` using normalized phases.
  - Persists the built image to `status.imageStatus.image`.
  - Creates a Workload resource from `workload-cr` if provided. Engines should not create Workload resources directly.

- **Naming consistency**: Reuse naming utilities and follow Kubernetes naming rules.
- **Error handling**: Wrap errors with context and use structured logs.
- **Resource management**: Make creation idempotent; clean up on failures when possible.
- **Status reporting**: Map engine-native statuses clearly; keep messages actionable.
- **Security**: Follow least-privilege RBAC and avoid cluster-wide permissions where not required.

## Testing Your Engine

- **Unit tests**: Validate lifecycle behavior and status mapping.
- **Integration tests**: Use envtest or a local cluster to validate resource creation and status retrieval.
- **End-to-end checks**: Ensure artifacts (image, Workload CR) are produced as expected.

Useful commands:
- `go test ./internal/controller/build/...`
- `kubectl get builds -n <ns> -w`
- `kubectl get workflows -n <ns>`     # Argo
- `kubectl get pipelineruns -n <ns>`  # Tekton

## Manual Testing

1. Deploy OpenChoreo in a development cluster.
2. Apply a Build CR that selects your engine via `spec.templateRef.engine`.
3. Watch the Build resource for status changes and conditions.
4. Inspect engine-specific resources (e.g., workflows or pipelineruns) in the build namespace.
5. After success, verify the image reference in `Build.status.imageStatus.image` and that a Workload CR is created if applicable.

## Troubleshooting

Common issues and hints:
- **Import cycles**: Keep engine code isolated; use shared utilities from names and engines packages.
- **Resource conflicts**: Ensure unique names and correct owner references.
- **Status sync**: Make sure `GetBuildStatus` reflects the actual engine state and terminal phases are recognized.
- **Missing CRDs**: Verify your engine’s CRDs are installed in the workflow plane cluster.

Debugging tips:
- Check controller logs in the control-plane namespace.
- Describe engine-native resources (e.g., Workflow, PipelineRun) for detailed status.
- Confirm RBAC permissions for the ServiceAccount used by the engine.

## Contributing

When adding a new build engine:
- Follow this guide and implement all required contract methods.
- Add comprehensive tests (unit, integration, and, if applicable, E2E).
- Update documentation including this guide and any engine-specific docs.
- Submit a PR describing the engine, requirements, and limitations.
- Consider backward compatibility and migration paths when changing defaults.

—

This document is maintained by the OpenChoreo core team. Last updated: 2025-08-20



File: docs/contributors/contribute.md
---
# Contributing to OpenChoreo Development

## Prerequisites

- Go version v1.24.0+
- Docker version 23.0+
- Make version 3.81+
- Kubernetes cluster with version v1.30.0+
- Kubectl version v1.30.0+
- Helm version v3.16.0+


To verify the tool versions, run the following command:
   ```sh
   ./check-tools.sh
   ```

## Getting Started

The OpenChoreo project is built using the [Kubebuilder](https://book.kubebuilder.io/) framework and uses Make for build automation.
After cloning the repository following the [github_workflow.md](github_workflow.md), run the following command to see all the available make targets:

```sh
make help
```

### Setting Up the k3d Kubernetes Cluster

For testing and development, we recommend using k3d (Kubernetes in Docker). The k3d development environment provides a multi-node cluster (1 server + 2 agents) that closely mimics production workload distribution.

#### Prerequisites for k3d Setup

Before starting, ensure you have:
- Docker 20.10+
- k3d 5.8+
- kubectl 1.32+
- Helm 3.12+

#### Quick Start Development Workflow

For a complete setup in one command:

```sh
make k3d
```

This will create the cluster, build all components, load images, and install OpenChoreo. This typically takes 5-15 minutes depending on your internet bandwidth.

#### Step-by-Step Setup

1. Create k3d cluster:

   ```sh
   make k3d.up
   ```

2. Build all OpenChoreo components:

   ```sh
   make k3d.build
   ```

3. Load component images into the cluster:

   ```sh
   make k3d.load
   ```

4. Install OpenChoreo (Control Plane, Data Plane, Workflow Plane, Observability Plane):

   ```sh
   make k3d.install
   ```

> [!NOTE]
> This command installs all planes in the single k3d cluster. You can install specific planes with `make k3d.install.<plane-name>` where plane-name is control-plane, data-plane, workflow-plane, or observability-plane.

5. Configure the DataPlane resource:

   OpenChoreo requires a DataPlane resource to deploy and manage workloads.

   ```sh
   make k3d.configure
   ```

6. Verify the deployment:

   ```sh
   make k3d.status
   ```

   Or check individual plane pods:
   ```sh
   kubectl --context k3d-openchoreo-dev get pods -n openchoreo-control-plane
   kubectl --context k3d-openchoreo-dev get pods -n openchoreo-data-plane
   ```

7. Run controller manager locally (for development):

   To run the controller manager locally during development:

   - First, scale down the existing controller deployment:
   ```sh
   kubectl --context k3d-openchoreo-dev -n openchoreo-control-plane scale deployment openchoreo-controller-manager --replicas=0
   ```

   - Then, run the manager with webhooks disabled:
   ```sh
   make go.run.manager ENABLE_WEBHOOKS=false
   ```

> [!TIP]
> The main controller runs as a deployment in the cluster. For rapid development iteration, you can run it locally while keeping other components in the cluster.

### Component-Specific Operations

- Build specific component: `make k3d.build.<component>` (controller, openchoreo-api, observer)
- Load specific component: `make k3d.load.<component>` (controller, openchoreo-api, observer)
- Update specific component: `make k3d.update.<component>` (rebuild, load, and restart)
- Upgrade specific plane: `make k3d.upgrade.<plane>` (control-plane, data-plane, workflow-plane, observability-plane)
- View logs: `make k3d.logs.<component>` (controller, openchoreo-api, observer)

### Cleanup

To delete the k3d cluster:

```sh
make k3d.down
```

### Port Access

Once the cluster is running, you can access services via localhost:

- **Control Plane UI/API**: http://openchoreo.localhost:8080
- **Data Plane Workloads**: http://localhost:19080 (kgateway)
- **Workflow Plane**: Argo Workflows at http://localhost:10081, Registry at http://localhost:10082
- **Observability**: Observer API at http://localhost:11080, OpenSearch at http://localhost:11082

### Building and Running the Binaries

This project comprises multiple binaries, mainly the `manager` binary and the `occ` CLI tool.
To build all the binaries, run:

```sh
make go.build
```

This will produce the binaries in the `bin/dist` directory based on your OS and architecture.
You can directly run the `manager` or `occ` binary this location to try out.

### Incremental Development

Rather using build and run the binaries every time, you can use the go run make targets to run the binaries directly.

- Running the `manager` binary:
  ```sh
  make go.run.manager ENABLE_WEBHOOKS=false
  ```

- Running the `occ` CLI tool:
  ```sh
  make go.run.occ GO_RUN_ARGS="version"
  ```
  
### Testing

To run the tests, you can use the following command:

```sh
make test
```
This will run all the unit tests in the project.

### Code Quality and Generation

Before submitting your changes, please ensure that your code is properly linted and any generated code is up-to-date.

#### Linting

Run the following command to check for linting issues:

```bash
make lint
```

To automatically fix common linting issues, use:

```bash
make lint-fix
```

#### Code Generation
After linting, verify that all generated code is up-to-date by running:

```bash
make code.gen-check
```

If there are discrepancies or missing generated files, fix them by running:

```bash
make code.gen
```

### Submitting Changes

Once all changes are made and tested, you can submit a pull request by following the [GitHub workflow](github_workflow.md).

## Additional Resources

- [Add New CRD Guide](adding-new-crd.md) - A guide to add new CRDs to the project.
- [Adding New MCP Tools](adding-new-mcp-tools.md) - A guide to add new tools to the OpenChoreo MCP server.



File: docs/contributors/development-process.md
---
This document describes the development process used by the OpenChoreo project.

# Overview

The OpenChoreo project uses an agile development process. We go through one week long development 
sprints to design and implement the roadmap items. 

Each Monday maintainers and contributors are expected to do the retrospective and planning and then continue with the week's assigned tasks.

# Issue Tracking
We use two GitHub boards to track issues.
- [OpenChoreo Release Management](https://github.com/orgs/openchoreo/projects/5) - Tracks higher level 
feature requirements, improvements and bugs. Features will be represented with type/epic issues. 
- [OpenChoreo Development](https://github.com/orgs/openchoreo/projects/7) - Development teams track 
tasks that will deliver new product features, bug fixes, improvements to the product. Only type/task issues will be added to this board.

# Issue Triage Process

This document outlines the issue triage process for contributors. The goal in issue triaging is to go through newly logged issues and incorporate them into the development process appropriately. Issue triaging will help to keep the open issue count and backlog healthy.

## Definitions

### Priority Labels

Priority labels are to be assigned by leads based on the severity and complexity of the issues. As an example, less severe but also less complex issues will have a high priority. Priority is also tied to the ETA as described below. Priority can change between triaging sessions and is affected by other external reasons.

* Priority/Highest  
  Issue should be dealt with immediately and added to the current sprint  
* Priority/High  
  Issue should be dealt with immediately and added to the next sprint  
* Priority/Normal  
  Issue should be dealt with within the current release  
* Priority/Low  
  It is ok to fix the issue in the next release

## Goals

* Keep an approved limited backlog for the current release   
  * Teams will have consistent flow of work  
  * Maintainers and contributors have the option to review effective backlog and make dynamic decisions  
* Keep the unattended issue count minimal  
  * Frequent triages would help maintainers and contributors to give attention to all the raised issues  
* Keep a healthy roadmap for next release  
  * PM will have a collection of vetted requests for the next release cycle planning

## Issue triage frequency

The issue triage process should happen at least once a week. If the issue count is not manageable, maintainers and contributors should plan to do several triage sessions to bring the issue count down.

## Issue triage process

Issue triaging should be done using Github issues. Maintainers and contributors should first filter issues based on the below criteria.

* Belongs to your Area label  
* Belongs to New Feature, Improvement, Bug issue types
* Not in 'OpenChoreo Release Management' project board

Then for each issue type follow the below sections

### Feature triage process

Type/Feature represents feature requests opened by the community. These requests should be first taken through the approval process according to this (./../proposals/README.md) document. If approval is not granted then the issue should be closed off with the reason. If approval is granted:
* Open a Type/Epic issue representing the new feature
* Add relevant details to the epic
* Add the epic to the [OpenChoreo Release Management](https://github.com/orgs/openchoreo/projects/5) project board and assign the milestone(v1.0.0, v1.1.0), area and priority.
* Close off the New Feature issue pointing to the epic

### Improvement triage process
* Initiate a discussion within the issue to decide the validity of the requirement
* If the improvement request is valid then assign the relevant milestone, area and priority.
* Add the improvement to the [OpenChoreo Release Management](https://github.com/orgs/openchoreo/projects/5) project board

### Bug Triage Process
* Initiate a discussion within the issue to decide the validity of the bug
* If the bug is valid then assign the relevant milestone, area and priority.
* 
* Add the bug to the [OpenChoreo Release Management](https://github.com/orgs/openchoreo/projects/5) project board



# Inside a Sprint

## Milestone Retrospective Meeting
> *Attendees*:
> - Development Team/Contributor
>
> *Time and Date*: First Monday of the sprint

Each team gets together and retrospects the last sprint

#### Key Tasks
- Review issues in PR Sent / In Review status and try to close them off
- Review issues still in progress and include a comment explaining why we could not finish them as planned and change the sprint to the current sprint
- Send updates to Slack with screencast when applicable for finished tasks

## Milestone Planning Meeting
> *Attendees*:
> - Development Team/Contributor
>
> *Time and Date*: First Monday of the sprint

Each team/contributor gets together and plans for the current sprint by picking tasks from the [OpenChoreo Development](https://github.com/orgs/openchoreo/projects/7) board backlog and moving them to the current iteration.

#### Key Tasks
- Pick tasks from backlog for the current sprint
- If there aren't enough tasks in the backlog go through the Release Management Board and pick epics/improvements/bugs based on priority
- For Epic and Improvement issues separately groom the issue and create subtasks accordingly and add subtasks to the OpenChoreo Development board backlog
- Add issues to the current iteration
- Add Area labels if not present
- Assign issues to contributors accordingly



File: docs/contributors/github_workflow.md
---
# GitHub Workflow Guide

This document provides a step-by-step guide on how to contribute to this repository.
Following this workflow ensures that contributions remain clean and consistent while staying up to date with the
upstream repository.

## Table of Contents

- [Forking the Repository](#forking-the-repository)
- [Cloning Your Fork](#cloning-your-fork)
- [Configuring Upstream](#configuring-upstream)
- [Syncing with Upstream](#syncing-with-upstream)
- [Creating and Rebasing Feature Branches](#creating-and-rebasing-feature-branches)
- [Resolving Conflicts](#resolving-conflicts)
- [Pushing Changes](#pushing-changes)
- [Before Opening a PR](#before-opening-a-pr)
- [PR Title Convention](#pr-title-convention)
- [DCO Sign-off](#dco-sign-off)
- [Merge Strategy](#merge-strategy)
- [FAQs](#faqs)

---

## Forking the Repository

1. Navigate to the repository on GitHub: [openchoreo/openchoreo](https://github.com/openchoreo/openchoreo).
2. Click the **Fork** button in the top-right corner.
3. This will create a fork under your GitHub account.

## Cloning Your Fork

To work on your fork locally:

```sh
# Replace <your-username> with your GitHub username
git clone https://github.com/<your-username>/openchoreo.git
cd openchoreo
```

## Configuring Upstream

To keep your fork up to date with the original repository:

```sh
# Add the upstream repository
git remote add upstream https://github.com/openchoreo/openchoreo.git

# Verify the remote repositories
git remote -v
```

Expected output:

```
origin    https://github.com/<your-username>/openchoreo.git (fetch)
origin    https://github.com/<your-username>/openchoreo.git (push)
upstream  https://github.com/openchoreo/openchoreo.git (fetch)
upstream  https://github.com/openchoreo/openchoreo.git (push)
```

## Syncing with Upstream

Before starting new work, sync your fork with the upstream repository:

```sh
git fetch upstream
git checkout main
git rebase upstream/main
```

If you have local commits on `main`, you may need to force-push:

```sh
git push -f origin main
```

## Creating and Rebasing Feature Branches

1. Create a new branch for your feature, based on `main`:
    ```sh
    git checkout -b feature-branch upstream/main
    ```

2. Make your changes and commit them.

3. Before opening a pull request, rebase against the latest upstream changes:
    ```sh
    git fetch upstream
    git rebase upstream/main
    ```

## Resolving Conflicts

If you encounter conflicts during rebasing:

1. Git will pause at the conflicting commit. Edit the conflicting files.

2. Stage the resolved files:
    ```sh
    git add <resolved-file>
    ```

3. Continue the rebase:
    ```sh
    git rebase --continue
    ```

4. If needed, repeat the process until rebase completes.

## Pushing Changes

Once rebased, push your changes:

```sh
git push -f origin feature-branch
```

> **Note**: Force-pushing is necessary because rebase rewrites history.

## Before Opening a PR

Before opening a pull request, make sure the following pass locally:

```sh
make lint
make code.gen-check
make test
```

For more details on building and testing, see the [contributing guide](contribute.md).

Open a pull request on GitHub targeting `main` in the upstream repository.

## PR Title Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.
PR titles must follow this format and are validated by the `lint-pr.yml` CI workflow. Since this repository uses
[squash merging](#merge-strategy), the PR title becomes the final commit message on `main`.

### Format

```
<type>(<scope>): <subject>
```

- **type** (required): The kind of change
- **scope** (optional): The area of the codebase
- **subject** (required): A short description starting with a lowercase letter

### Types

| Type       | Purpose                                  |
|------------|------------------------------------------|
| `feat`     | New feature                              |
| `fix`      | Bug fix                                  |
| `docs`     | Documentation only                       |
| `refactor` | Code restructure (no behavior change)    |
| `test`     | Adding or correcting tests               |
| `chore`    | Maintenance tasks                        |
| `ci`       | CI/CD changes                            |
| `build`    | Build system or dependencies             |
| `perf`     | Performance improvement                  |
| `style`    | Code style (formatting, no logic change) |
| `revert`   | Reverting a previous commit              |

### Scopes

| Scope        | Covers                                |
|--------------|---------------------------------------|
| `api`        | `cmd/openchoreo-api`, `api/v1alpha1/` |
| `controller` | `internal/controller/*`               |
| `cli`        | `cmd/choreoctl`, `cmd/occ`            |
| `helm`       | `install/helm/*`                      |
| `deps`       | `go.mod`, dependencies                |

Scope is optional. If a change spans multiple areas, either use the most relevant scope or omit it.

### Examples

```
feat(controller): add ComponentRelease reconciler
fix(api): handle missing organization gracefully
chore(deps): bump sigs.k8s.io/controller-runtime
docs: add DCO sign-off instructions
ci: add CodeQL security scanning workflow
refactor(controller): extract common reconciler logic
```

## DCO Sign-off

All commits must be signed off to certify that you have the right to submit the code under the project's open-source
license. This is enforced by the [DCO](https://developercertificate.org/) check on pull requests.

Add the `-s` flag when committing:

```sh
git commit -s -m "feat(api): add component validation"
```

This appends a `Signed-off-by` line to your commit message:

```text
Signed-off-by: Your Name <your.email@example.com>
```

To sign off all commits automatically, you can set up a git alias:

```sh
git config --add alias.c "commit -s"
```

### Fixing a failed DCO check

If you forgot to sign off your commits, you can amend the last commit:

```sh
git commit --amend -s --no-edit
git push -f origin feature-branch
```

Or sign off all commits in your branch:

```sh
git rebase --signoff upstream/main
git push -f origin feature-branch
```

## Merge Strategy

This repository enforces **squash merging** as the only merge strategy. When a pull request is merged, all commits in
the PR are squashed into a single commit on `main`.

### How it works

- The **PR title** becomes the commit message on `main`, with the PR number automatically appended
  (e.g., `feat(api): add component validation (#1234)`).
- The **individual commit messages** from the PR are preserved in the commit body for reference.
- Contributors can commit freely during development without worrying about keeping a clean commit history — the squash
  merge handles that automatically.

### What this means for contributors

- Focus on writing a clear, descriptive PR title that follows the [PR title convention](#pr-title-convention).
- You do not need to manually squash commits before merging.
- Use as many commits as you need during development (work-in-progress, review feedback, fixups, etc.).
- The `lint-pr.yml` CI workflow validates that PR titles follow the conventional commit format.

---

## FAQs

### Why do we use rebase instead of merge?

Rebasing keeps history linear, making it easier to track changes and avoid unnecessary merge commits. This is especially
useful to keep a clean commit history.

### Can I rebase after opening a pull request?

Yes, but you will need to force-push (`git push -f origin feature-branch`). GitHub will automatically update the pull
request with your new changes.

### How can I undo a rebase?

If something goes wrong during rebasing, you can use:

```sh
git rebase --abort
```

or, if you've already completed the rebase but want to undo it:

```sh
git reset --hard ORIG_HEAD
```

> **Warning**: This will discard changes that were part of the rebase.

Alternatively, you can use git reflog to find the commit before the rebase and reset to it:

```sh
git reflog
```

Identify the commit before the rebase (e.g., HEAD@{3}), then reset to it:

```sh
git reset --hard HEAD@{3}

```

> **Warning**: This will discard changes that were part of the rebase.



File: docs/contributors/release.md
---
# Releasing a new version of OpenChoreo

The release process of OpenChoreo is tracked through a GitHub issue with a release issue template.
Please follow the steps below to create a new release issue and complete the release process.

1. Go to the [Release Issue creation template](https://github.com/openchoreo/openchoreo/issues/new?template=06_release_template.md)
2. Update the issue title to the desired release. Example: `Release: v1.4.0`
3. Create the issue and assign it to yourself.
4. Follow the checklist in the issue to complete the release process.




File: docs/crds/README.md
---
# OpenChoreo CRDs Design Documentation

This directory contains design documentation for OpenChoreo's Custom Resource Definitions (CRDs). Each document provides detailed information about specific CRD's purpose, design patterns, API reference, and usage examples.

## List of CRDs

- [**RenderedRelease**](renderedrelease.md) - Applies component-specific resources to the dataplane that are generated via bindings



File: docs/crds/renderedrelease.md
---
# RenderedRelease CRD Design

The RenderedRelease CRD serves as the deployment resource for all component types in OpenChoreo. It takes component-specific resources generated by binding controllers and applies them to data plane clusters.

## Purpose

The RenderedRelease controller is responsible for deploying finalized Kubernetes resources to data plane clusters. It provides full resource lifecycle management, including creation, updates, tracking, and cleanup of resources across data plane clusters.

## Architecture Flow

The RenderedRelease controller is part of OpenChoreo's multi-plane architecture, where the control plane manages developer intent and the data plane runs the actual workloads.

```mermaid
graph TD
    A[Component] --> B[ComponentRelease]
    B --> C[ReleaseBinding]
    C --> H[RenderedRelease]

    subgraph "Control Plane"
        A
        B
        C
        H
    end

    subgraph "Data Plane"
        I[Deployments]
        J[Services]
        K[ConfigMaps]
        L[CronJobs]
        M[HTTPRoute]
    end

    H --> I
    H --> J
    H --> K
    H --> L
    H --> M

    style H fill:#e8f5e8
```

**Flow Explanation:**
1. **Component Definition**: Developers create Component resources that define the type, ownership, and configuration of their applications
2. **ComponentRelease**: An immutable snapshot is created containing the frozen ComponentType, Traits, and Workload specifications
3. **ReleaseBinding**: For each target environment, a ReleaseBinding binds a ComponentRelease to an Environment with environment-specific configuration overrides
4. **RenderedRelease Generation**: The ReleaseBinding controller renders complete Kubernetes manifests using the rendering pipeline and creates RenderedRelease resources
5. **Data Plane Deployment**: The RenderedRelease controller takes the rendered resources from RenderedRelease CRDs and applies them to the target data plane clusters

## RenderedRelease Controller Process

The RenderedRelease controller implements a reconciliation process that ensures reliable deployment and lifecycle management of Kubernetes resources.

```mermaid
graph TD
    A[RenderedRelease Reconciliation Triggered] --> B{RenderedRelease Being Deleted?}
    B -->|Yes| C[Run Finalizer Logic]
    B -->|No| D[Ensure Finalizer Added]
    
    D --> E[Get DataPlane Client]
    E --> F[Convert Resources to Objects]
    F --> G[Ensure Namespaces Exist]
    G --> H[Apply Resources to Data Plane]
    
    H --> I[Discover Live Resources]
    I --> J[Find Stale Resources]
    J --> K[Delete Stale Resources]
    
    K --> L[Update RenderedRelease Status]
    L --> M{Resources Transitioning?}
    M -->|Yes| N[Requeue with ProgressingInterval]
    M -->|No| O[Requeue with Interval]
    
    C --> P[Cleanup All Resources]
    P --> Q[Remove Finalizer]
    Q --> R[RenderedRelease Deleted]
    
    style G fill:#e1f5fe
    style H fill:#e3f2fd
    style I fill:#f3e5f5
    style J fill:#fff3e0
    style L fill:#e8f5e8
    style C fill:#ffe6e6
    style M fill:#fff9c4
```

**Process Explanation:**

1. **Namespace Pre-creation**: Before applying any resources, the controller identifies all namespaces referenced by the resources and ensures they exist in the data plane. This prevents deployment failures due to missing namespaces.

2. **Resource Application**: The controller converts the raw resource definitions into Kubernetes objects, adds tracking labels for ownership and lifecycle management, and applies them to the target data plane cluster using server-side apply.

3. **Live Resource Discovery**: The controller queries the data plane to discover all resources currently managed by this RenderedRelease. It uses GroupVersionKind (GVK) discovery to find resources across different API groups, ensuring complete inventory tracking.

4. **Stale Resource Cleanup**: The controller identifies any resources that exist in the data plane but are no longer present in the current RenderedRelease specification. These orphaned resources are safely deleted to prevent resource accumulation and drift.

5. **Status Update**: Finally, the controller updates the RenderedRelease status with a complete inventory of all applied resources, maintaining accurate tracking information for future reconciliation cycles and providing visibility into the deployment state.

## Key Features

### Universal Resource Support
- **Any Kubernetes Resource**: Supports deployment of any Kubernetes resource type through `runtime.RawExtension`
- **CRD Agnostic**: Automatically handles third-party CRDs (Gateway API, Cilium, etc.) without code changes
- **Future-proof**: New resource types work without controller modifications

### Resource Management
- **Inventory Tracking**: Maintains complete resource inventory in status for lifecycle management
- **Stale Resource Cleanup**: Prevents resource accumulation by cleaning up orphaned resources
- **Label-based Ownership**: Consistent resource tracking across reconciliations

### Namespace Management
- **Automatic Creation**: Pre-creates namespaces before applying resources to prevent deployment failures
- **Create-Only Pattern**: Namespaces are created but never deleted by the renderedrelease controller
- **Audit Labels**: Tracks which release created each namespace for operational visibility

## CRD Structure

### RenderedReleaseSpec

```go
type RenderedReleaseSpec struct {
    // Owner identifies the component that owns this release
    Owner RenderedReleaseOwner `json:"owner"`
    
    // EnvironmentName is the target environment for deployment
    EnvironmentName string `json:"environmentName"`
    
    // Resources contains the Kubernetes resources to deploy
    Resources []Resource `json:"resources,omitempty"`
    
    // Interval is the watch interval for stable resources (defaults to 5m)
    // Set to 0 to disable requeuing
    Interval *metav1.Duration `json:"interval,omitempty"`
    
    // ProgressingInterval is the watch interval for transitioning resources (defaults to 10s)
    // Set to 0 to disable requeuing
    ProgressingInterval *metav1.Duration `json:"progressingInterval,omitempty"`
}

type RenderedReleaseOwner struct {
    // ProjectName is the project containing the component
    ProjectName string `json:"projectName"`
    
    // ComponentName is the specific component name
    ComponentName string `json:"componentName"`
}

type Resource struct {
    // ID is a unique identifier for the resource within the release
    ID string `json:"id"`
    
    // Object is the complete Kubernetes resource definition
    Object *runtime.RawExtension `json:"object"`
}
```

### RenderedReleaseStatus

```go
type RenderedReleaseStatus struct {
    // Resources tracks successfully applied resources
    Resources []ResourceStatus `json:"resources,omitempty"`
    
    // Conditions represent the latest available observations
    Conditions []metav1.Condition `json:"conditions,omitempty"`
}

type ResourceStatus struct {
    // ID corresponds to resource ID in spec
    ID string `json:"id"`
    
    // Group, Version, Kind identify the API details
    Group   string `json:"group"`
    Version string `json:"version"`
    Kind    string `json:"kind"`
    
    // Name and Namespace identify the resource in the data plane
    Name      string `json:"name"`
    Namespace string `json:"namespace,omitempty"`
    
    // Status captures the entire .status field of the resource applied to the data plane
    Status *runtime.RawExtension `json:"status,omitempty"`
    
    // LastObservedTime stores the last time the status was observed
    LastObservedTime *metav1.Time `json:"lastObservedTime,omitempty"`
}
```

## Controller Architecture

The RenderedRelease controller implements a reconciliation process:

### Resource Application
- Converts raw resource definitions to unstructured objects
- Adds tracking labels to all resources:
  - `openchoreo.dev/managed-by`: "renderedrelease-controller"
  - `openchoreo.dev/rendered-release-resource-id`: Resource ID from spec
  - `openchoreo.dev/rendered-release-uid`: RenderedRelease UID for ownership tracking
  - `openchoreo.dev/rendered-release-name`: Name of the RenderedRelease that manages the resource
  - `openchoreo.dev/rendered-release-namespace`: Namespace of the RenderedRelease that manages the resource
- Applies resources to data plane using server-side apply

### Live Resource Discovery
- Queries data plane for all resources managed by this RenderedRelease
- Uses GVK (GroupVersionKind) discovery combining:
  - Current desired resources (from spec)
  - Previously applied resources (from status)
  - Well-known Kubernetes resource types (safety net)
- Supports discovery of any CRDs without hardcoded lists

### Stale Resource Cleanup
- Identifies resources that exist in data plane but not in current spec
- Implements Flux-style inventory cleanup to prevent resource accumulation
- Deletes orphaned resources (e.g., ConfigMaps removed from spec)

### Namespace Pre-creation
- Identifies all namespaces referenced by resources before deployment
- Create namespaces with tracking labels:
  - `openchoreo.dev/created-by`: "renderedrelease-controller" (audit trail)
  - `openchoreo.dev/rendered-release-name`: Name of the creating RenderedRelease
  - `openchoreo.dev/rendered-release-namespace`: Namespace of the creating RenderedRelease
  - `openchoreo.dev/rendered-release-uid`: UID of the creating RenderedRelease
  - `openchoreo.dev/environment`: Target environment name
  - `openchoreo.dev/project`: Project name from the RenderedRelease owner
- Create-only: namespaces are never deleted by renderedrelease controller

### Status Update
- Updates RenderedRelease status with inventory of applied resources
- Extracts and stores the `.status` field from live resources in the data plane
- Tracks `LastObservedTime` for each resource, updating only when status changes
- Maintains complete tracking for future cleanup operations

### Resource Transitioning Detection
The controller detects transitioning states to adjust reconciliation frequency:

**Transitioning Resources Check:**
- **Deployments**: Checks unavailable replicas, ready replicas, and updated replicas
- **StatefulSets**: Checks ready, available, current, and updated replicas
- **Pods**: Checks for Pending or Unknown phases
- **Other Resources**: Considered stable (ConfigMaps, Secrets, Services, etc.)

**Reconciliation Intervals:**
- **Stable Resources**: Uses `interval` field (default 5m) with 20% jitter
- **Transitioning Resources**: Uses `progressingInterval` field (default 10s) with 20% jitter
- **Jitter**: Prevents thundering herd by adding random delay to requeue intervals
- **Disable Requeue**: Set interval to 0 to disable automatic reconciliation

## Integration with Binding Controllers

The RenderedRelease controller serves as the deployment target for all binding controllers.

### Binding Controller Integration

Binding controllers are expected to:
1. **Render Manifests**: Create complete Kubernetes manifests from binding + class templates
2. **Create RenderedRelease**: Generate RenderedRelease resources with rendered manifests
3. **Set Owner References**: Establish proper garbage collection relationships
4. **Delegate Deployment**: Let the RenderedRelease controller handle all data plane interactions

## Resource Lifecycle Management

### Finalizer Handling

The RenderedRelease controller implements cleanup through finalizers:

**Finalizer**: `openchoreo.dev/dataplane-cleanup`

**Finalization Process**:
1. **Status Update**: Sets "Finalizing" condition
2. **Resource Discovery**: Finds all managed resources in data plane
3. **Cleanup**: Deletes all managed resources
4. **Verification**: Retries if resources still exist (5-second intervals)
5. **Finalizer Removal**: Removes finalizer once cleanup is complete

### Resource Tracking and Cleanup

- **Proactive Cleanup**: Removes resources no longer in spec during normal reconciliation
- **Discovery**: Tracks resources across GVK changes
- **Label-based Management**: Uses consistent labeling for resource ownership
- **Graceful Deletion**: Handles resource deletion with proper verification

## Example Usage

### Basic RenderedRelease Resource

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: RenderedRelease
metadata:
  name: my-service-dev
  namespace: my-namespace
spec:
  owner:
    projectName: my-project
    componentName: my-service
  environmentName: dev
  resources:
    - id: deployment
      object:
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: my-service
          namespace: my-namespace
        spec:
          replicas: 2
          selector:
            matchLabels:
              app: my-service
          template:
            metadata:
              labels:
                app: my-service
            spec:
              containers:
                - name: app
                  image: my-service:v1.0.0
                  ports:
                    - containerPort: 8080
    - id: service
      object:
        apiVersion: v1
        kind: Service
        metadata:
          name: my-service
          namespace: my-namespace
        spec:
          selector:
            app: my-service
          ports:
            - port: 80
              targetPort: 8080
```

### RenderedRelease with Complex Resources

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: RenderedRelease
metadata:
  name: my-app-prod
  namespace: my-namespace
spec:
  owner:
    projectName: my-project
    componentName: my-app
  environmentName: prod
  interval: 10m  # Check stable resources every 10 minutes
  progressingInterval: 5s  # Check transitioning resources every 5 seconds
  resources:
    - id: deployment
      object:
        apiVersion: apps/v1
        kind: Deployment
        # ... deployment spec
    - id: service
      object:
        apiVersion: v1
        kind: Service
        # ... service spec
    - id: hpa
      object:
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        # ... HPA spec
    - id: pdb
      object:
        apiVersion: policy/v1
        kind: PodDisruptionBudget
        # ... PDB spec
    - id: network-policy
      object:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        # ... NetworkPolicy spec
    - id: gateway-route
      object:
        apiVersion: gateway.networking.k8s.io/v1
        kind: HTTPRoute
        # ... HTTPRoute spec
```

## Design Benefits

### Unified Deployment Model
- **Single Controller**: One controller handles all component types
- **Consistent Behavior**: Same deployment semantics across Services, ScheduledTasks, WebApplications, APIs
- **Simplified Maintenance**: Reduced code duplication and operational complexity

### Robust Resource Management
- **Complete Lifecycle**: From creation to cleanup with proper tracking
- **Leak Prevention**: Stale resource detection and cleanup
- **Multi-environment**: Supports deployment across multiple data plane clusters

### Extensibility
- **Future-proof**: Supports new resource types without code changes
- **CRD Support**: Automatically handles custom resources
- **Template Flexibility**: Supports any Kubernetes resource pattern


## Implementation Details

### Controller Location
- **Main Controller**: [`internal/controller/renderedrelease/controller.go`](../../internal/controller/renderedrelease/controller.go)
- **Finalization**: [`internal/controller/renderedrelease/controller_finalize.go`](../../internal/controller/renderedrelease/controller_finalize.go)
- **Status Tracking**: [`internal/controller/renderedrelease/controller_status.go`](../../internal/controller/renderedrelease/controller_status.go)
- **CRD Definition**: [`api/v1alpha1/renderedrelease_types.go`](../../api/v1alpha1/renderedrelease_types.go)

### Key Dependencies
- **Environment/DataPlane**: For target cluster configuration
- **Binding Controllers**: As resource providers
- **Kubernetes Client**: For data plane resource management

### Configuration
- **Finalizer**: `openchoreo.dev/dataplane-cleanup`
- **Manager Labels**: `openchoreo.dev/managed-by=renderedrelease-controller`
- **Resource ID Labels**: `openchoreo.dev/rendered-release-resource-id`
- **RenderedRelease UID Labels**: `openchoreo.dev/rendered-release-uid`
- **RenderedRelease Name Labels**: `openchoreo.dev/rendered-release-name`
- **RenderedRelease Namespace Labels**: `openchoreo.dev/rendered-release-namespace`



File: docs/proposals/0142-standardize-build-conditions.md
---
# Standardize build conditions for build workflow

**Authors**:  
@chalindukodikara

**Reviewers**:  
@Mirage20

**Created Date**:  
2025-04-07

**Status**:  
Approved

**Related Issues/PRs**:  
https://github.com/openchoreo/openchoreo/issues/142
https://github.com/openchoreo/openchoreo/pull/149

---

## Summary
Currently, the build controller adds conditions only when a step is completed, resulting in three possible states: `InProgress`, `Succeeded`, and `Failed`. This approach makes it difficult for clients—such as the CLI and UI—to determine the full set of build workflow steps ahead of time.

As of now, the workflow consists of three steps: Clone, Build, and Push. However, additional steps may be introduced in the future. This would require client-side code changes to accommodate new steps, which is not ideal. To improve usability and make the system more extensible and predictable, we propose standardizing how workflow steps are represented in the resource status.

---

## Motivation

The current condition model only reflects steps that have already occurred, making it challenging for clients to understand the complete workflow structure. This tightly couples clients with the current set of steps, requiring changes when the workflow evolves.

By standardizing step representation:
- Clients can always expect a complete and consistent list of workflow steps.
- It eliminates the need for clients to change their logic when steps are added or removed.
- It improves maintainability and aligns with long-term goals like switching CI systems (e.g., Argo to GitHub Actions).
---

## Goals

- Define a standardized way to represent workflow/pipeline steps in the resource status.
- Update the build controller to work for the new model.

---

## Non-Goals

None

---

## Impact


- **Build Controller**: Requires changes to populate and update workflow step conditions.
- **CLI / UI**: Should be updated to rely on the standardized condition names and structure, rather than dynamically checking for specific conditions.
---


## Design

### Overview

The controller will initialize all workflow steps in the resource status with a default condition when the build starts. Each step will have four possible states: `Queued`, `InProgress`, `Succeeded`, and `Failed`.

Each step condition will use a consistent naming pattern: `Step<StepName>Succeeded`, and will include a clear `Reason`:

- **Queued**: Step is pending execution
- **InProgress**: Step is currently running
- **Succeeded**: Step completed successfully
- **Failed**: Step execution failed

To clearly differentiate these from other types of conditions, the prefix `Step` will be used.

This model ensures long-term compatibility, as new steps can be introduced without requiring client changes. It also supports future CI engine changes, as the representation remains stable.

---

### Naming Convention and Examples

| Step       | Condition Name        | State       | Reason        | Status |
|------------|-----------------------|-------------|----------------|--------|
| Clone      | `StepCloneSucceeded`  | Queued      | `Queued`       | False  |
|            |                       | InProgress  | `Progressing`  | False  |
|            |                       | Succeeded   | `Succeeded`    | True   |
|            |                       | Failed      | `Failed`       | False  |
| Build      | `StepBuildSucceeded`  | Queued      | `Queued`       | False  |
|            |                       | InProgress  | `Progressing`  | False  |
|            |                       | Succeeded   | `Succeeded`    | True   |
|            |                       | Failed      | `Failed`       | False  |
| Push       | `StepPushSucceeded`   | Queued      | `Queued`       | False  |
|            |                       | InProgress  | `Progressing`  | False  |
|            |                       | Succeeded   | `Succeeded`    | True   |
|            |                       | Failed      | `Failed`       | False  |

> **Note:** New steps introduced in the future should follow the same `Step<StepName>Succeeded` convention for consistency.



File: docs/proposals/0159-control-plane-data-plane-separation.md
---
# Control Plane and Data Plane Separation

**Authors**:
@chalindukodikara

**Reviewers**:
@Mirage20
@sameerajayasoma

**Created Date**:
2025-04-10

**Status**:
Approved

**Related Issues/PRs**:
https://github.com/openchoreo/openchoreo/issues/159

---

## Summary

This proposal addresses the architectural separation of OpenChoreo's Control Plane (CP) and Data Plane (DP) to enable
multi-cluster deployments. Currently, both CP and DP reside within the same Kubernetes cluster, limiting deployment
flexibility. This proposal introduces multiple approaches for secure, efficient communication between a centralized
Control Plane and multiple distributed Data Planes across different Kubernetes clusters.

---

## Motivation

In real-world scenarios, user deployments may span across multiple Data Planes hosted on various Kubernetes
clusters—either self-managed or provided by different cloud vendors. The current architecture, where CP and DP coexist
in the same cluster, cannot support these multi-cluster deployments.

Solving this problem will introduce a key feature required for an Internal Developer Platform (IDP), adding substantial
value to OpenChoreo and its users by enabling:

- Geographic distribution of workloads
- Multi-cloud deployments
- Enhanced security through network isolation
- Better resource utilization and scaling

---

## Goals

1. Establish a **lightweight and secure communication mechanism** between CP and DPs
2. Ensure the **desired state** is applied and the **actual state** is retrievable from DPs
3. **Reconcile resources** when changes are detected in DPs
4. Ensure that **status updates** are reconciled from the Control Plane, maintaining it as the single source of truth (
   etcd in CP)
5. **Minimize the resource load** on Data Planes

---

## Impact

- **Control Plane Controllers**: Will need modifications to support remote Data Plane communication
- **DataPlane CRD**: Will require updates to store connection credentials and configuration
- **CLI/UI**: May need updates to display multi-cluster status information
- **Installation**: New deployment models for separated CP/DP architecture
- **Security**: New authentication and authorization mechanisms for CP-DP communication

---

## Design

### Solution Overview

This proposal presents three main approaches for CP-DP separation, each with different trade-offs:

### Solution 1: Direct Control Plane Access to Data Plane

In scenarios where CP and DP exist within the same virtual network (local setups or cloud VPCs), the Control Plane can
directly access the Data Plane using its credentials.

![Direct Access Architecture](0159-assets/direct-access.png)

**Advantages:**

- Easier to implement and test in local environments
- Ideal for development setups
- No additional components required

**Considerations:**

- Users might be reluctant to expose DP API server
- HTTP calls might be slower than persistent connections
- Each resource call directly hits the API server
- Requires periodic reconciliation to detect changes

#### Solution 1.1: Extending to Cloud with Mesh Networking

Use Tailscale or similar mesh networking solutions to securely expose DP clusters to CP without public API server
exposure.

**Advantages:**

- Secure exposure of DP API server
- Works across network boundaries
- No public endpoint exposure required

#### Solution 1.2: Agent-Based Communication Model

A more scalable option using an agent-based communication model where:

1. Users apply resources to the Control Plane via CLI or UI
2. Control Plane controllers communicate with agents over persistent WebSocket/gRPC channels
3. Agents running in Data Planes connect to the CP server
4. CP applies and reads YAML manifests through the agent connection

![Agent-Based Architecture](0159-assets/agent-based.png)

**Advantages:**

- Proven architecture (already in use within Choreo)
- More secure and cloud-friendly
- Pull-based model (agents initiate connection)
- Works across any network topology

### Solution 2: GitOps with Secondary Repository

This approach uses a secondary GitHub repository for generated Kubernetes YAML manifests:

1. Users store OpenChoreo abstractions in one repository
2. CP generates Kubernetes YAMLs and stores them in a secondary repository
3. FluxCD in the Data Plane periodically retrieves and applies these resources

![GitOps Architecture](0159-assets/gitops.png)

**Advantages:**

- Reconciliation offloaded to FluxCD
- Additional version control and rollback capability
- GitOps-native approach

**Considerations:**

- Still requires reading cluster status (via agent or API)
- Additional complexity in managing secondary repository
- Requires structured YAML organization (folders/branches per project/component/environment)
- Local setup requires GitHub repository

### Agent-Based Communication Implementation Options

If adopting Solution 1.2 or Solution 2, we need an agent-based communication model. Options include:

#### Option 1: Custom Implementation

Build our own WebSocket/gRPC-based agent system tailored to OpenChoreo's needs.

#### Option 2: ClusterNet

[ClusterNet](https://clusternet.io/docs/introduction/) provides cluster management capabilities:

- Deploy and coordinate applications to multiple clusters
- Single set of APIs in hosting cluster
- Built-in agent system

![ClusterNet Architecture](https://clusternet.io/images/clusternet-arch.png)

#### Option 3: Open Cluster Management (OCM)

[Open Cluster Management](https://open-cluster-management.io/docs/concepts/architecture/) provides:

- **Hub Cluster**: Lightweight cluster hosting controllers and services
- **Klusterlet**: Agent that pulls prescriptions from hub and reconciles managed clusters
- Pull-based model where managed clusters reach out to hub

![OCM Architecture](https://github.com/open-cluster-management-io/OCM/raw/main/assets/ocm-arch.png)

Since ClusterNet and OCM can directly reconcile the DP cluster, secondary GitHub storage becomes unnecessary.

---

## Recommendation

**Solution 1 (Direct Access)** has been implemented as the initial approach, which provides a solid foundation for local development and environments where CP and DP share network connectivity.

For future enhancements to support more complex deployment scenarios, we recommend **Solution 1.2 (Agent-Based Communication Model)** with **Option 3 (Open Cluster Management)** as the agent framework. This would provide:

1. **Security**: Pull-based model where Data Planes initiate connections
2. **Flexibility**: Works across any network topology without exposing API servers
3. **Maturity**: OCM is a CNCF project with proven stability
4. **Extensibility**: Can be enhanced with GitOps patterns later if needed
5. **Backward Compatibility**: Can coexist with the current direct access implementation

The direct access implementation serves as the foundation, with agent-based communication as the natural evolution for production multi-cluster deployments.

---

## Implementation Plan

Issue: https://github.com/openchoreo/openchoreo/issues/188

1. **Phase 1**: Implement direct access for local development
2. **Phase 2**: Integrate Open Cluster Management for agent-based communication
3. **Phase 3**: Add support for multiple Data Planes per Control Plane
4. **Phase 4**: Optional GitOps integration for users who prefer that workflow



File: docs/proposals/0186-integrate-external-idp.md
---
# Using an External Identity Provider to Secure APIs in OpenChoreo

**Authors**:  
_@vajiraprabuddhaka_

**Reviewers**:  
_@Mirage20 @sameerajayasoma_

**Created Date**:  
_2025-04-16_

**Status**:  
_Submitted_

**Related Issues/PRs**:  
_https://github.com/openchoreo/openchoreo/issues/186_

---

## Summary

This proposal introduces the capability for OpenChoreo to integrate with external Identity Providers (IdPs) such as Asgardeo, Auth0, Okta, Azure AD, or AWS Cognito to secure APIs exposed through the platform. Currently, OpenChoreo's API security model relies on built-in authentication mechanisms, which limits enterprise adoption where organizations have standardized on external identity management systems.

This enhancement enables platform engineers to define external identity providers in OpenChoreo and allows application developers to utilize those providers for securing their APIs. The integration will work seamlessly with OpenChoreo's multi-plane architecture, where identity provider configurations are managed in the control plane and enforced in data plane clusters through the API gateway infrastructure.

The proposal enables organizations to leverage their existing identity infrastructure investments while maintaining OpenChoreo's declarative, GitOps-compatible approach to API management.

---

## Motivation

Enterprise organizations have standardized on external identity providers (Asgardeo, Auth0, Okta, Azure AD, AWS Cognito) for user authentication and authorization across their applications. To enable OpenChoreo adoption in enterprise environments, APIs exposed through the platform must integrate seamlessly with these existing identity management systems.

This integration is essential for organizations to maintain centralized user management, enforce consistent security policies, ensure compliance requirements, and leverage their existing identity infrastructure investments. Without external IdP support, organizations cannot fully adopt OpenChoreo as their internal developer platform.

---

## Goals

### Security requirements

- **Environment level isolation**.
  - The primary way we should support environment-level isolation is by having two different identity tenants (or maybe two different IDPs)
  - Shouldn’t be very opinionated; users should have the capability to do whatever they want by dealing with claim validations.
    - Can use single IDP across multiple environments by bringing up client details (client_id) into the OpenChoreo Endpoint level.
- **Across component isolation**.
  - If the same Identity Provider is shared across multiple components, the same token should not be used to access multiple components.
- **Operation-level access control**.
  - If a component has multiple operations, it should be possible to provide access control using scopes.

---

## Non-Goals

- Securing the OpenChoreo system APIs using an external Identity provider.

---

## Impact

- **APIClass CRD**: Place where Platform engineers can configure external identity providers.
- **ServiceBinding Controller**: Generate the necessary gateway artifacts to propagate the external identity provider configuration to the API gateway.

---

## Design

### Overview

External identity provider integration leverages OpenChoreo's existing APIClass CRD. Platform engineers define external IdP configurations in APIClass resources, while application developers reference the APIClass when they are creating their services.

### APIClass Configuration

The existing `AuthenticationPolicy` structure in APIClass will be extended to support external identity providers:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: APIClass
metadata:
  name: enterprise-api-class
  namespace: acme
spec:
  restPolicy:
    defaults:
      authentication:
        type: jwt
        jwt:
          issuer: "https://auth.company.com"
          jwks: "https://auth.company.com/.well-known/jwks.json"
          audience: ["api://choreo-apis"]
```

### Service Configuration

Application developers reference the APIClass when exposing their APIs:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Service
metadata:
  name: user-service
  namespace: acme
spec:
  className: enterprise-api-class
  workloadName: user-service-workload
  apis:
    user-api:
      className: enterprise-api-class
      rest:
        backend:
          basePath: /api/v1/users
          port: 8080
        exposeLevels:
        - Organization
```

### Control Flow

1. **Platform Engineer**: Creates APIClass with external IdP configuration
2. **Application Developer**: References APIClass in Service resource
3. **ServiceBinding Controller**: Generates gateway configurations with IdP settings
4. **Data Plane Gateway**: Enforces authentication using external IdP for API requests

---



File: docs/proposals/0200-openchoreo-developer-concepts.md
---
# OpenChoreo Developer Concepts

**Authors**:  
@sameerajayasoma
@Mirage20  

**Reviewers**:  

**Created Date**:  
2025-04-19

**Status**:  
Approved

**Related Issues/PRs**:  
[Issue #200 – openchoreo/openchoreo](https://github.com/openchoreo/openchoreo/issues/200)

---

## Summary
This proposal defines a set of developer-facing abstractions for OpenChoreo (Project, Component, API, and WorkloadSpec) to declaratively model application architecture and runtime behavior. It suggests a GitOps-compatible workflow for managing these resources in version control, while also introducing a control plane API to support interactive operations via CLI and UI. The design supports both monorepo and multi-repo setups, enabling the reuse of the same source code across multiple components with distinct runtime contracts.

## Goals
- Enable developers to define Projects, Components, and APIs using declarative YAML files.
- Provide a clear way to declare a component’s runtime contract (e.g., endpoints, connections, etc) separate from source code.
- Ensure all declarations are easily managed in Git repositories and are compatible with GitOps workflows (e.g., Argo CD, Flux) for automated reconciliation and promotion.
- Provide recommended patterns for organizing declarations across mono- and multi-repository setups.
- Allow a single codebase to back multiple components, each with its own workload configuration.
- Expose an API server in the OpenChoreo control plane to support CLI, UI, and CI systems, complementing GitOps with interactive and event-driven workflows.

## Developer-facing abstractions
The following is a set of high-level, declarative constructs that enable developers to model project or application structure, runtime contracts, and connectivity without needing to manage low-level infrastructure details.

OpenChoreo introduces a set of high-level, Kubernetes-native abstractions that help developers and platform engineers structure, deploy, and expose cloud-native applications with clarity and control. These abstractions are explicitly separated to address concerns like identity, runtime behavior, API exposure, version tracking, and environment-specific deployment.

### Project
A Project is a logical grouping of related components that collectively define an application or bounded context. It serves as the main organizational boundary for source code, deployments, and network policies.
Projects:
- Define team or application-level boundaries.
- Govern internal access across components.

A project defines deployment isolation, visibility scope, and governs how components communicate internally and with external systems via ingress and egress gateways.

### Component 
A component represents a deployable piece of software, such as a backend service, frontend webapp, background task, or API proxy.

Each Component:
- Defines its identity within a Project.
- Declares its type (e.g., service, webapp, task, api).
  - Specifies the component type-specific settings (cron expression, replica sets, API mgt stuff) 
- Refers to a source code location (e.g., Git repo, image registry).
  - I.e, Workload of the component.

### Component Types
Each Component in OpenChoreo is assigned a type that determines its behavior, settings, and how it is deployed and exposed. A Component Type captures the high-level intent of the component. Whether it runs continuously, executes on a schedule, proxies an API, or represents a managed resource, such as a database.

OpenChoreo includes several built-in Component Types, each with its own set of expected behaviors and type-specific settings:

#### WebApp
A web-facing application that serves frontend assets or handles HTTP traffic. It may expose ports and routing paths via a gateway.
#### Service
A backend service, often HTTP or gRPC-based, that serves as an internal or external API provider.
#### ScheduledTask
A task that runs on a cron schedule, ideal for background jobs or periodic automation.
#### ManualTask
A placeholder for components that involve manual execution or human workflow, often used for approval gates or ops procedures.
#### ProxyAPI
An API proxy that exposes an upstream backend through OpenChoreo’s built-in API gateway with support for versioning, throttling, and authentication.


Component Types are pluggable. Platform teams can define their own types to represent custom workloads, third-party services, or golden-path abstractions, each with their own schema and runtime behavior.

### Workload 
A Workload captures the runtime contract of a Component within a DeploymentTrack. It defines how the component runs: its container image, ports, environment variables, and runtime dependencies.
Workloads:
- They are versioned and linked to a specific track.
- Can change frequently (e.g., after every CI build).

The WorkloadDescriptor defines the runtime contract of the component. What OpenChoreo needs to know in order to wire, expose, and run it. It describes:
- What ports and protocols does the component expose?
- What are the connection dependencies (e.g., databases, queues, other component endpoints)?
- What container image should be deployed?

It is typically maintained along with the source code of a component. 

If we decouple the OpenChoreo component from its workload descriptor, then we can support the goal of linking a single source code to multiple OpenChoreo components. This is what we have in WSO2 Choreo SaaS.

By combining a component’s type, its settings, and an optional workload, OpenChoreo provides a consistent and extensible model for defining, deploying, and operating software components across various environments.

### API
An API describes how a component’s endpoint is exposed beyond its Project. This includes HTTP routing, versioning, authentication, rate limits, and scopes.

APIs:
- Are optional — many components may remain internal.
- Can be independently versioned.
- Enable controlled exposure (organization-wide or public) and integration into API gateways or developer portals.

Both Service and ProxyAPI Component types can expose APIs. 

### DeploymentTrack
A DeploymentTrack represents a line of development or a delivery stream for a component. It can be aligned with a Git branch (main, release-1.0, feature-xyz), an API version (v1, v2), or any other meaningful label that denotes evolution over time.

This is optional when getting started or for simpler use cases. If omitted, it is assumed to belong to the default track (default).

### Environments 
An Environment represents a target runtime space — such as dev, staging, or prod. It encapsulates infrastructure-specific configuration like cluster bindings, gateway setups, secrets, and policies.
Environments:
- Are where actual deployments occur.
- May have constraints or validations (e.g., only approved workloads may run in prod).

### Deployments
A Deployment binds a specific Workload (and optionally an API) to an Environment within a given track. It represents the act of deploying a concrete version of a component to a specific environment.

Deployments:
- Are the unit of rollout and promotion.
- Track the exact workload/API deployed in each environment.
- Enable progressive delivery by reusing the same workload across environments (e.g., dev → staging → prod).

The Deployment is always derived, never written by hand
- Developers author Component, Workload (?), and optionally API
- GitOps or CI/CD workflows generate a Deployment by linking the current Workload + API + Track + Environment
- Promotion means copying or regenerating the Deployment with the same Workload in a different environment

### Why are Component, Workload and Type-specific Settings separated?
Separating these concerns improves clarity, reusability, and GitOps alignment:
- Component defines identity, ownership, and deployment intent—what the unit of software is.
- Workload captures how the component runs—image, ports, environment—often generated or updated by CI.
- Type-specific Settings configure how the component behaves based on its type—e.g., a cron schedule for a task, or routing rules for an API.

## YAML file format
Projects, components and APIs are Kubernetes CRDs. We can make them less complicated for developers and PEs to maintain. 

This section describes the shape and semantics of these kinds. 

### Namespaces and Organizations
There is a 1:1 mapping between OpenChoreo organizations and Kubernetes namespaces in the OpenChoreo control plane. 

We create a K8s namespace for each OpenChoreo organization. This is a cluster-scoped resource. All other resources within this organization are created as namespace-scoped resources.

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Organization
metadata:
  name: acme

---
apiVersion: openchoreo.dev/v1alpha1
kind: Organization
metadata:
  name: default
```

The following project is part of the Acme organization. 
```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  name: hello-project
  namespace: acme
spec:
  owner:
    organization: acme
```

The `metadata.namespace` is a mandatory field unless it is in the default organization or namespace. See the semantics of the resource with the name default: [https://github.com/openchoreo/openchoreo/issues/227](https://github.com/openchoreo/openchoreo/issues/227)

The `spec.organization` field is an optional field and OpenChoreo operator can add it if it is not present.

#### The default organization
By default, OpenChoreo creates an organization called “default” which gets mapped to the Kubernetes “default” namespace. This default namespace will always be there in a K8s cluster and it cannot be deleted AFAIK. 

The beauty of this default org and the corresponding default K8s namespace is that you can omit the namespace field in CRs. You will see this in the following samples. 

### Custom resource(CR) naming scope
In OpenChoreo, all first-class developer abstractions — Organization, Project, Component, and API — are modeled as Kubernetes Custom Resources (CRs). 

These resources follow a global naming model within the control plane:
- Organization CR names must be unique within the K8s cluster where the OpenChoreo control plane resides.
- Project CR names must be unique within an Organization (K8s namespace)
- Component CR names must be globally unique within an Organization (K8s namespace)
- API CR names must be globally unique within an Organization (K8s namespace)

### Immutable fields
Certain spec fields in Project, API and Component CRs are immutable after creation. Consider the following example. 

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: reading-list
  namespace: acme
spec:
  owner:
    organizationName: acme
    projectName: hello-world
```

The fields spec.organization and spec.project are immutable after creation. The OpenChoreo admission webhooks enforce this. 

We may make them mutable later. Who knows :) 

### Kubernetes labels
Typically, labels are used for querying, filtering, indexing and automation. In this design, developers are not required to add labels, but they are useful to have them. Therefore, OpenChoreo admission webhooks can mutate the resources to add labels during the resource creation process. 

This is what the developer writes:
```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: reading-list
  namespace: acme
spec:
  owner:
    projectName: hello-project
  type: service
```

This is what gets stored in etcd:
```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: reading-list
  namespace: acme
  lables:
    openchoreo.dev/org: acme
    openchoreo.dev/project: hello-project
    openchoreo.dev/component: reading-list\
    openchoreo.dev/type: service

 ... # Other generated fields

spec:
    owner:
      organizationName: acme
      projectName: hello-world
  type: service
```

### Project
A logical boundary that groups related components and APIs. It defines runtime isolation and controls ingress/egress via gateways. 

The following YAML represents a project. 
```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  name: hello-project
```

Currently, all fields in the spec section are optional. A project sample with the spec section:
```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  name: hello-project
spec:
  deploymentPipelineRef: default
```

The organization field is also optional. The default organization is called “default” which maps to the “default” namespace of the Kubernetes cluster. AFAIK, this default namespace will always be there in a Kubernetes cluster and it cannot be deleted. 

Here is a sample with the organization name. If you want to use a different organization, then you would have to add two fields:
- `metadata.namepsace` 
- `spec.organiation`

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Project
metadata:
  name: hello-project
  namespace: abc
spec:
  organization: abc
```

### Component 
A component abstraction in OpenChoreo is defined by three parts:
1) Declares the identity of the component, including name, project and organization. Declares whether OpenChoreo should build the image or not (BYOR vs BYOI).
   - This is the OpenChoreo component kind, just like the project kind
2) Describes how the component should be executed at runtime, including what it exposes (Endpoints) and depends on (Connections). 
   - Current Choreo SaaS component.yaml or Score’s workload spec.
3) Describes the component type-specific runtime settings.


The obvious choice is to inline all three parts in a single Component CR. But that would make the CR too complicated to author and maintain. I believe separating these concerns improves clarity, reusability, and GitOps alignment. We can consider inlining them later if needed.

#### Part 1: Component CR
This is the OpenChoreo Component CR. It declares the identity of the component, including name, project and organization. It also declares whether OpenChoreo should build the image or not (BYOR vs BYOI).

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: reading-list
  namespace: acme
spec:
  owner:
    organizationName: acme
    projectName: hello-project
  type: service
  Build:
    Repository:
      App Path:  /service-go-reading-list
      Revision:
        Branch:  main
      URL:       https://github.com/openchoreo/sample-workloads
    Template Ref:
      Name:  google-cloud-buildpacks
```

The `spec.build` section is optional. If it is omitted, then it is assumed to be BYOI (Bring Your Own Image) and OpenChoreo will not attempt to build the image. This is useful if you are using an external CI/CD system to build and push images.

#### Part 2: WorkloadDescriptor CR
This is the workload descriptor CR. It describes how the component should be executed at runtime, including what it exposes (Endpoints) and depends on (Connections). In other words, it describes the runtime contract of the component in a programming language-agnostic way.

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workload
metadata:
  name: go-reading-list-service
  namespace: default
spec:
  containers:
    main:
      image: localhost:30003/default-reading-list-service:default-8ecbb654
  endpoints:
    reading-list-api:
      port: 8080
      schema:
        content: "openapi: 3.0.1\ninfo:\n  title: Choreo Reading List\n  description: ... "
  owner:
    componentName: reading-list-service
    projectName: default
```

#### Part 3: Type-specific Settings
This section describes the component type-specific runtime settings. The settings vary based on the component type (e.g., service, webapp, task, api).

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Service
metadata:
  name: reading-list-service
  namespace: default
spec:
  apis:
    reading-list-api:
      className: default
      rest:
        backend:
          basePath: /api/v1/reading-list
          port: 8080
        exposeLevels:
        - Public
      type: REST
  className: default
  owner:
    componentName: reading-list-service
    projectName: default
  workloadName: go-reading-list-service
```

### Workload descriptor
A Workload descriptor captures the runtime contract of a Component within a DeploymentTrack. It defines how the component runs: its container image, ports, environment variables, and runtime dependencies. This is typically maintained along with the source code of a component and the Workload CR is created by a CI/CD system or GitOps operator.

We expect the CI system to create or update the Workload CR after a successful build and push of the container image. The Workload CR is linked to a specific Component and DeploymentTrack.

Here is a sample workload descriptor. The current design expects a `workload.yaml` file in the source code repo. We'll come up with a spec for the workload descriptor later.

```yaml
# OpenChoreo Workload Descriptor
# This file defines how your workload exposes endpoints and connects to other services.
# It sits alongside your source code and gets converted to a Workload Custom Resource (CR).
apiVersion: openchoreo.dev/v1alpha1

# Basic metadata for the workload
metadata:
  # +required Name of the workload
  name: go-reading-list-service

# +optional Incoming connection details for the component
# Endpoints define the network interfaces that this workload exposes to other services
endpoints:
  - # +required Unique name for the endpoint
    # This name will be used when generating the managed API and as the key in the CR map
    name: reading-list-api
    # +required Numeric port value that gets exposed via the endpoint
    port: 8080
    # +required Type of traffic that the endpoint is accepting
    # Allowed values: REST, GraphQL, gRPC, TCP, UDP, HTTP, Websocket
    type: REST
    # +optional The path to the schema definition file
    # This is applicable to REST, GraphQL, and gRPC endpoint types
    # The path should be relative to the workload.yaml file location
    schemaFile: docs/openapi.yaml

connections: # Not finalized yet
  - name: book-service
    resourceRef: ...
  - name: reading-list-db 
    resourceRef: ...
```




File: docs/proposals/0245-introduce-build-plane.md
---
# Introduce BuildPlane for Build Workloads

**Authors**:  
@chalindukodikara

**Reviewers**:  
@Mirage20  
@sameerajayasoma

**Created Date**:  
2025-06-12

**Status**:  
Approved

**Related Issues/PRs**:  
[Issue #245 – openchoreo/openchoreo](https://github.com/openchoreo/openchoreo/issues/245)

---

## Summary

Currently, all Argo Workflows run on a fixed Kubernetes cluster. This rigid setup limits flexibility in configuring build infrastructure, which can lead to inefficient resource usage or violation of security boundaries.

This proposal introduces a new `BuildPlane` kind that allows users to define a dedicated cluster for executing build workloads. With this, users can:

- Isolate build workloads from runtime environments to improve security and reliability.
- Scale build infrastructure independently of application runtime clusters.
- Select a specific DataPlane or an external cluster to serve as the build environment.

---

## Motivation

Enabling builds to run on any specified cluster gives users greater control over their CI/CD pipelines. This is especially useful when infrastructure separation is required for governance, compliance, or scalability.

---

## Goals

- Allow users to configure the target cluster for Argo Workflows, enabling control over where builds are executed.
- Provide a mechanism to specify container registry configurations for pushing built images.

---

## Non-Goals

- Multi-BuildPlane scheduling and prioritization logic are deferred to a future phase.
- This proposal does not contain image pull logic; it focuses solely on build execution and image pushing.

---

## Impact

- **Build Controller**: Needs updates to support scheduling builds on a specified `BuildPlane`.
- **Build Plane Client**: Logic must be standardized to work across both DataPlane and BuildPlane clusters.
- **DataPlane Resource**: Push registry configuration will be removed; the API will be refactored accordingly.
- **Installation Scripts**: The installation process will need to support creation of the `BuildPlane` resource.

---

## Design

A `BuildPlane` represents an execution environment for build-related workloads (e.g., building container images, running tests, publishing artifacts). It is backed by a Kubernetes cluster and integrated via Argo Workflows.

It operates via Argo Workflows within its own Kubernetes cluster, separate from both the Control Plane and Data Plane. Each `BuildPlane` is registered using a `BuildPlane` CR, which contains the connection details needed by the Control Plane to delegate build executions.

**Key Benefit**:  
Resource isolation: build workloads do not compete with runtime workloads for cluster resources.

> **Note**: A DataPlane cluster can act as a BuildPlane if explicitly configured.

---

### Considerations

1. Each Component is linked to a single `BuildPlane`.
2. An organization may have multiple `BuildPlanes`, but must define one as the default.
   - Future enhancements (e.g., project-level overrides) can customize this default.
3. All container registries listed in the `BuildPlane` are used for image pushing.
   - Even if not all registries are linked to the component being built.

> **Initial Limitation**: Only one BuildPlane per organization is supported in the initial implementation. Multi-BuildPlane feature will be introduced in future phases.

---

### CRDs Definitions

#### BuildPlane

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: BuildPlane
metadata:
   name: example-buildplane
spec:
   # References to ContainerRegistry CRs used for image push operations
   registries:
      - prefix: docker.io/namespace
        secretRef: docker-push-secret
      - prefix: ghcr.io/namespace
        secretRef: ghcr-push-secret
   kubernetesCluster:
      name: test-cluster
      credentials:
         apiServerUrl: https://api.example-cluster
         caCert: <base64-ca-cert>
         clientCert: <base64-client-cert>
         clientKey: <base64-client-key>
```

#### DataPlane

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: DataPlane
metadata:
   name: example-dataplane
spec:
   # Reference to ContainerRegistry CR used for pulling images
   registry:
      prefix: docker.io/namespace
      secretRef: dockerhub-pull-secret
   kubernetesCluster:
      name: test-cluster
      credentials:
         apiServerUrl: https://api.example-cluster
         caCert: <base64-ca-cert>
         clientCert: <base64-client-cert>
         clientKey: <base64-client-key>
```



File: docs/proposals/0482-modular-architecture-proposal.md
---
# Modular architecture for OpenChoreo

**author**:
@lakwarus

**Reviewers**: 
@sameerajayasoma
@binura-g
@manjulaRathnayaka

**status**: 
Draft

**created**: 
2025-09-29

**issue**: 
[Issue #0482 – openchoreo/openchoreo](https://github.com/openchoreo/openchoreo/discussions/482)

---

# Summary

This proposal introduces a **modular architecture for OpenChoreo**, enabling adopters to start with a **secure, production-ready Kubernetes foundation** and incrementally add modules as their needs grow.  

The design provides two entry points:
- **OpenChoreo Secure Core (Cilium Edition):** Full Zero Trust security, traffic encryption, and support for all add-on modules.  
- **OpenChoreo Secure Core (Generic CNI Edition):** Basic Kubernetes networking with limited add-on support, providing a lower-friction entry with a natural upgrade path to the Cilium Edition.  

This modular approach lowers adoption friction, supports production use cases from day one, and creates a **land-and-expand path** toward a full Internal Developer Platform (IDP).

---

# Motivation

Adopters of Internal Developer Platforms (IDPs) typically seek two things:
1. **Low-friction entry:** Start simple, prove value quickly.  
2. **Scalable growth path:** Add features as the organization matures.  

With earlier approaches (e.g., monolithic designs), challenges arose:
- Complex architecture → slow feature delivery and high infra cost.  
- Adoption required multiple teams to align, leading to long, difficult cycles.  

A modular OpenChoreo addresses these issues by:
- Delivering a **default Secure Core** that is immediately valuable.  
- Allowing adopters to **add modules incrementally**, instead of an “all-or-nothing” platform.  
- Creating a **clear upgrade path** from initial adoption → enterprise-grade platform without replatforming.  

---

# Goals

- Provide a **modular open-source architecture** that adopters can consume incrementally.  
- Offer a **secure Kubernetes foundation** with built-in abstractions (Org, Projects, Components, Environments).  
- Support both **Cilium** and **generic CNIs** to meet adopters where they are.  
- Deliver **tangible benefits** to Developers (simplified onboarding) and Platform Engineers (Zero Trust, control, governance).  
- Establish a **progressive adoption path**: Secure Core → Core Modules (CD + Observe) → Expansion (CI, API, Elastic) → Enterprise (Guard, Vault, AI).  

---

# Non-Goals

- Targeting **individual hobbyist developers**.  
- Replacing existing CI/CD pipelines; instead, OpenChoreo integrates with them.  

---

# Impact

### Positive
- **Lower entry barrier** → easy for teams to adopt.  
- **Progressive expansion path** → natural growth into advanced modules.  
- **Clearer messaging** → modular story is easier for the community to understand.  
- **Improved adoption experience** → Devs and PEs get immediate value.  

### Negative / Risks
- Operating two Secure Core flavors (Cilium vs Generic) adds **support overhead**.  
- Migration tooling will be required for adopters moving from Generic → Cilium.  
- If adopters stay on Generic Edition, they miss advanced features (e.g., governance).  

---

# Design

## OpenChoreo Secure Core (Default Platform)

### Description
- Zero Trust–enabled Kubernetes baseline.  
- Supports key abstractions: **Org, Project, Components, Environments**.  
- Provides network isolation, CLI, UI, and AI-assisted lifecycle management.  
- Minimal operational footprint.  

### Technology
- Kubernetes  
- CNI: Cilium (Cilium Edition) or Generic (Calico, Flannel, cloud-provider CNI)  
- Ingress Gateway (NGINX IC)  
- External Secrets Controller ([external-secrets.io](https://external-secrets.io/latest/))  
- Thunder + Envoy GW (for CP APIs)  
- Cert-Manager  
- CLI / UI / AI Webapp  

### Topology
- Single cluster, single environment by default.  
- OpenChoreo CRDs support **multi-environment definitions** within the same cluster.  
- No built-in GitOps (external GitOps can be plugged in).  
- No CI/CD, Observability, or API Gateway in the base.  

### Benefits
**For Developers**  
- Secure, isolated projects without Kubernetes complexity.  
- CLI + UI to create/manage projects & components.  
- Reduced friction compared to raw Kubernetes.  

**For Platform Engineers**  
- Enforce Zero Trust.  
- Simplified cluster onboarding.  
- Higher-level controls vs vanilla Kubernetes.  

---

## Secure Core Flavors

### Secure Core (Cilium Edition)
- Cilium is the mandatory CNI.  
- Enables full Zero Trust networking with traffic encryption.  
- Supports **all add-on modules**, including advanced observability and governance.  
- Target: Enterprises and advanced teams building toward a full IDP.  

### Secure Core (Generic CNI Edition)
- Runs with generic CNI (Calico, Flannel, cloud-provider).  
- Provides basic network isolation (no encryption).  
- Limited add-on compatibility:  
  - Observability: basic logs & metrics only.  
  - Governance & Security: not supported.  
- Other add-ons (CD, CI, API Gateway, Elastic, Automate) supported.  
- Target: Teams that want a quick start with existing network stacks.  

---

## Why Not Just Vanilla Kubernetes?

- **Abstraction:**  
  - *Vanilla K8s:* Infrastructure-level primitives (pods, YAML).  
  - *OpenChoreo Secure Core:* Enterprise-ready abstractions (Org, Project, Component, Environment).  

- **Zero Trust Security:**  
  - *Vanilla K8s:* Must configure manually.  
  - *OpenChoreo Secure Core:* Built-in Zero Trust (Cilium Edition).  

- **Multi-Environment Support:**  
  - *Vanilla K8s:* Namespaces + pipelines.  
  - *OpenChoreo Secure Core:* CRDs for structured environments.  

- **Enterprise Support:**  
  - *Vanilla K8s + Cilium:* DIY or expensive vendor contracts.  
  - *OpenChoreo Secure Core:* Community-supported OSS (with commercial support available separately).  

---

## Add-On Modules

| **Module** | **Name** | **Description** | **Cilium Edition** | **Generic Edition** |
|------------|----------|-----------------|---------------------|----------------------|
| CD | OpenChoreo CD Plane | GitOps-driven Continuous Delivery (Argo CD). | ✅ | ✅ |
| CI | OpenChoreo Workflow Plane | CI pipelines, build packs, container scans. | ✅ | ✅ |
| Observability | OpenChoreo Observe Plane | Logs, metrics, tracing, cell diagrams. | ✅ Full | ⚠️ Basic only |
| API Gateway | OpenChoreo API Gateway Plane | External & internal API management. | ✅ | ✅ |
| Automation | OpenChoreo Automate Plane | General-purpose pipelines. | ✅ | ✅ |
| Elasticity | OpenChoreo Elastic Plane | Autoscaling & scale-to-zero (KEDA). | ✅ | ✅ |
| Governance | OpenChoreo Guard Plane | Compliance, egress control, approvals. | ✅ | ❌ |
| Registry | OpenChoreo Registry Plane | Embedded/external registry (Harbor). | ✅ | ✅ |
| Vault | OpenChoreo Vault Plane | Secret management (Vault/OpenBao). | ✅ | ✅ |
| AI Gateway | OpenChoreo AI Gateway Plane | Secure LLM/AI inference APIs. | ✅ | ✅ |
| AI Intelligence | OpenChoreo Intelligence Plane | AI-powered ops/dev workflows. | ✅ | ✅ |

---

## Adoption Path

1. **Step 1 – Start with Secure Core**  
   - Cilium Edition: Full Zero Trust, encryption, add-ons supported.  
   - Generic Edition: Basic isolation, limited add-ons.  

2. **Step 2 – Add Core Modules (CD + Observe)**  
   - GitOps delivery + environment promotion.  
   - Advanced observability (Cilium) or basic logs/metrics (Generic).  

3. **Step 3 – Expand (Build, API, Elastic)**  
   - Add CI, API Gateways, autoscaling.  

4. **Step 4 – Enterprise (Guard, Vault, AI)**  
   - Governance, secrets, AI modules.  
   - Only Cilium Edition supports full governance.  

---

# Industry Use Cases

- **FinTech:** Secure Core (Cilium) + CD + Guard + Observe → Compliance & Zero Trust.  
- **SaaS Startup:** Secure Core (Generic) + Elastic + Build → Cost-optimized, quick start.  
- **Healthcare:** Secure Core (Cilium) + Guard + Vault + Observe → HIPAA-ready.  
- **AI Platforms:** Secure Core + API + AI Gateway + Intelligence → Secure AI delivery.  

---

# Next Steps
- Gather community feedback on modular design.  
- Align roadmap with **OpenChoreo 1.0 release**.  
- Define packaging for Secure Core + optional modules.  



File: docs/proposals/0537-introduce-component-type-definitions.md
---
# Introduce Component Type Definitions

**Authors**:
@ChathurangaKCD

**Reviewers**:

**Created Date**:
2025-10-17

**Status**:
Submitted

**Related Issues/PRs**:
[Issue #537 – openchoreo/openchoreo](https://github.com/openchoreo/openchoreo/issues/537)

---

## Summary

This proposal introduces **ComponentTypeDefinitions with Addons** to replace OpenChoreo's current rigid component types (Services, WebApps, ScheduledTasks). The new approach enables platform engineers to define atomic, composable component types using CEL-based templates that stay close to Kubernetes primitives, while addons provide reusable cross-cutting capabilities. This design maintains a simplified developer experience through a single Component CRD while giving platform engineers full control and extensibility.

---

## Motivation

OpenChoreo's current component types (**Services**, **WebApps**, and **ScheduledTasks**) provide developer-centric abstractions where developers have direct control over the entire Deployment specification. While this gives developers flexibility, it creates several challenges:

- **Over-abstraction from Kubernetes APIs**: Current component types mask native Kubernetes resources, making the mental model harder for Kubernetes-savvy users to understand OpenChoreo's Components.

- **Limited platform engineer control**: ComponentClasses can only override portions of developer-defined Deployment specs. Platform engineers cannot enforce organizational policies, resource limits, or deployment configurations as templates that developers instantiate.

- **No composition model**: Platform engineers cannot define their own component types by combining Kubernetes primitives, OpenChoreo concepts, and external CRDs of other tools they may be using.

- **No environment-specific overrides**: There is no way to override or patch environment-specific parameters (like resource limits or replica counts) in a structured, validated manner.

As a result, platform engineers lack the control needed to enforce organizational standards, and they may be forced to bypass OpenChoreo entirely if their requirements do not fit into one of OpenChoreo's opinionated component types.

---

## Goals

- **Extensibility**: Platform engineers can model organizational needs without forking or bypassing OpenChoreo. Addons enable cross-cutting capabilities (storage, networking, security) to be reused across component types.

- **Alignment with Kubernetes**: Reduces friction by staying consistent with native APIs, making it easier for Kubernetes-savvy teams to understand and adopt OpenChoreo.

- **Developer Experience**: Developers get a consistent, simplified interface (single Component CRD) with guardrails, while platform engineers retain full control. OpenChoreo's developer abstractions like endpoints, connections and config schemas are retained without restricting PE control.

- **Reusability**: Define ComponentTypeDefinitions and Addons once, compose them in multiple ways across different components.

---

## Non-Goals

- **Replace Kubernetes primitives**: This proposal does not aim to abstract away or replace Kubernetes resources. Instead, it works with them to provide a higher-level interface while maintaining compatibility.

- **Support multiple primary workload resources**: Each ComponentTypeDefinition is limited to a single primary workload resource. The ComponentTypeDefinition must declare a `workloadType` field (one of: `deployment`, `statefulset`, `cronjob`, `job`), and the primary workload resource's `id` must match this `workloadType`. Additional supporting resources (Services, HPAs, PDBs, etc.) can be defined in the resources section and via addons.

---

## Impact

This proposal introduces new CRDs and controller support:

- New CRDs: `ComponentTypeDefinition` (v1alpha1), `Addon` (v1alpha1), and `ComponentDeployment` (v1alpha1)
- New `v1alpha1` version of the `Component` CRD with `componentType` and `addons[]` fields
- New controllers for rendering ComponentTypeDefinitions with CEL templating and applying addon composition

---

## Design

### Overview

This design introduces three core mechanisms explained below with concrete examples:

### 1. Template-Based ComponentTypeDefinitions

ComponentTypeDefinitions use templates to generate Kubernetes resources dynamically, staying close to native K8s APIs while adding parameterization.

- Instead of static YAML, use **CEL (Common Expression Language)** templates that pull data from multiple sources, including developer inputs, the workload spec, and references to all resources defined within the template.

- Types, validations and expressions from CEL allow UIs to be autogenerated from the template, enabling dynamic forms for these resources in the OpenChoreo portal (and in the CLI).

- **Workload Type Constraint**: Each ComponentTypeDefinition must explicitly declare a `workloadType` (one of: `deployment`, `statefulset`, `cronjob`, `job`). The ComponentTypeDefinition must define exactly one primary workload resource whose `id` matches the declared `workloadType`. Additional supporting resources (Service, HPA, PDB, etc.) can be included in the resources section. When creating a Component, the `componentType` field uses the format `{workloadType}/{componentTypeDefinitionName}` (e.g., `deployment/web-app`).

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ComponentTypeDefinition
metadata:
  name: web-app
  namespace: default
spec:
  # Workload type - must be one of: deployment, statefulset, cronjob, job
  workloadType: deployment

  # Schema defines what developers can configure
  schema:
    parameters:
      # Static across environments and exposed as inputs to the developer when creating a Component of this type
      # Examples provided after Component definition section

    envOverrides:
      # Can be overriden per environment via ComponentDeployment by the PE
      # Examples provided after Component definition section

  # Templates generate K8s resources dynamically
  resources:
    - id: deployment
      template:
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: ${metadata.name}
        spec:
          selector:
            matchLabels: |
              ${metadata.podSelectors}
          template:
            metadata:
              labels: |
                ${merge({"app": metadata.name}, metadata.podSelectors)}
            spec:
              terminationGracePeriodSeconds: ${spec.lifecycle.terminationGracePeriodSeconds}
              containers:
                - name: app
                  image: ${build.image}
                  imagePullPolicy: ${spec.lifecycle.imagePullPolicy}
                  command: ${spec.runtime.command}
                  args: ${spec.runtime.args}
                  ports: |
                    ${workload.endpoints.map(e, {"containerPort": e.port})}
                  resources:
                    requests:
                      cpu: ${spec.resources.requests.cpu}
                      memory: ${spec.resources.requests.memory}
                    limits:
                      cpu: ${spec.resources.limits.cpu}
                      memory: ${spec.resources.limits.memory}

    - id: hpa
      includeWhen: ${spec.autoscaling.enabled}
      template:
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        metadata:
          name: ${metadata.name}
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: ${metadata.name}
          minReplicas: ${spec.autoscaling.minReplicas}
          maxReplicas: ${spec.autoscaling.maxReplicas}
          metrics:
            - type: Resource
              resource:
                name: cpu
                target:
                  type: Utilization
                  averageUtilization: ${spec.autoscaling.targetCPUUtilization}

    - id: pdb
      includeWhen: ${spec.autoscaling.enabled}
      template:
        apiVersion: policy/v1
        kind: PodDisruptionBudget
        metadata:
          name: ${metadata.name}
        spec:
          selector:
            matchLabels:
              app: ${metadata.name}
          minAvailable: 1
```

**Key insight:** Templates access data from different sources at different times:

- `${metadata.name}` - Component instance name
- `${metadata.namespace}` - Component instance namespace
- `${metadata.labels}` - Component instance labels
- `${metadata.annotations}` - Component instance annotations
- `${metadata.podSelectors}` - Platform-injected pod selectors (e.g., `openchoreo.io/component-id`, `openchoreo.io/environment`, `openchoreo.io/project-id`) for component identity and environment tracking
- `${spec.*}` - Developer configuration from Component (merged parameters + envOverrides)
- `${build.*}` - Build context from Component's build field
- `${workload.*}` - Application metadata extracted from source repo at build time

**forEach support for generating multiple resources:**

ComponentTypeDefinitions support `forEach` to generate multiple instances of a resource template. This is useful for scenarios like creating multiple ConfigMaps from a list of configurations:

```yaml
resources:
  - id: config
    forEach: ${spec.configurations}
    var: config
    template:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${metadata.name}-${config.name}
      data: |
        ${config.data}
```

In this example, if the controller injects configurations into the template context:

```yaml
configurations:
  - name: app-config
    data:
      LOG_LEVEL: "info"
      FEATURE_FLAG: "enabled"
  - name: db-config
    data:
      DB_HOST: "postgres.default.svc"
      DB_PORT: "5432"
```

The system will generate two ConfigMaps: `checkout-service-app-config` and `checkout-service-db-config`, each with their respective data.

### 2. Addons for Composability

- Addons are atomic, reusable units that modify or augment the underlying Kubernetes resources without requiring separate component type definitions for every variation.
- This avoids combinatorial explosion of rigid component types (no need for "web-app-with-pvc" vs "web-app-with-X", instead PEs can define their own addons that developers can compose into their Components for cross-cutting capabilities).
- OpenChoreo can provide a set of pre-built Addons for common use cases, and PEs can write their own as well. Developers should be able to discover these via the OpenChoreo console/CLI.

Addons can:

- **Create** new resources (PVCs & Volumes, PDBs, ResourceQuotas, Certificates, etc.)
- **Modify (patch)** existing resources (add volumes, sidecars, init containers, topology spread constraints, pod security policies, etc)

### 3. Component CRD - Single Unified Resource

Instead of generating multiple CRDs, developers use a single **Component** CRD with a `componentType` field and `addons[]` array:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: checkout-service
spec:
  # Select which ComponentTypeDefinition to use
  componentType:
    kind: ComponentType
    name: deployment/web-app

  # Parameters from ComponentTypeDefinition (oneOf schema based on componentType).
  # Like all other parameters, these are typed, validated and can have default values (so can be optional when necessary).
  parameters:
    lifecycle:
      terminationGracePeriodSeconds: 60
      imagePullPolicy: IfNotPresent
    resources:
      requests:
        cpu: 200m
        memory: 512Mi
      limits:
        cpu: 1000m
        memory: 1Gi
    autoscaling:
      enabled: false
      minReplicas: 2
      maxReplicas: 10
      targetCPUUtilization: 80

  # Addon instances (developer chooses which addons to use)
  addons:
    # Create PVC and add volume to pod
    - name: persistent-volume-claim
      instanceName: app-data
      config:
        volumeName: app-data-vol
        mountPath: /app/data
        size: 50Gi
        storageClass: fast

    # Add logging sidecar for file-based logs
    - name: add-file-logging-sidecar
      instanceName: app-logs
      config:
        logFilePath: /var/log/app/application.log
        containerName: app

  # Build field (added to CRD schema by OpenChoreo, populated by developer)
  build:
    repository:
      url: https://github.com/myorg/checkout-service
      revision:
        branch: main
      appPath: .
    templateRef:
      name: docker
      parameters:
        - name: docker-context
          value: .
        - name: dockerfile-path
          value: ./Dockerfile
```

**Component CRD Schema:**

The Component CRD uses a **oneOf schema** for the `parameters` field based on the `componentType`:

- When `componentType: web-app`, the `parameters` field schema is the **merged schema** of the ComponentTypeDefinition's `parameters` and `envOverrides`
- This allows developers to configure both static parameters and environment-overridable settings in one place
- At runtime, these are split: `parameters` remain static, `envOverrides` can be overridden in ComponentDeployment
- Templates access merged values via `${spec.*}` (e.g., `${spec.lifecycle.terminationGracePeriodSeconds}`, `${spec.resources.requests.cpu}`)

**Workload Spec (extracted from source repo at build time):**

- The workload spec will be a developer-facing resource that's committed to the application's source repository (as the "workload.yaml").
- This will contain OpenChoreo developer concepts like `endpoints`, `connections`, and `config schema(?)` and will be proceed by the system and uses it as (automatic) inputs to the ComponentTypeDefinitions when composing the final Kubernetes resources.

```yaml
# workload.yaml in source repo
endpoints:
  - name: api
    type: http
    port: 8080
    schemaPath: ./openapi/api.yaml

connections:
  - name: productcatalog
    type: api
    params:
      projectName: gcp-microservice-demo
      componentName: productcatalog
      endpoint: grpc-endpoint
    inject:
      env:
        - name: PRODUCT_CATALOG_SERVICE_ADDR
          value: "{{ .host }}:{{ .port }}"
configSchema: ... # Design TBD
```

This workload spec is available as `${workload.*}` in ComponentTypeDefinition templates, so that PEs can also build additional capabilities based on the values provided here by the developers.

**Example ComponentTypeDefinition schema with parameters and envOverrides:**

```yaml
schema:
  parameters:
    # Component-level parameters - static across environments
    runtime:
      command: array<string> | default=[]
      args: array<string> | default=[]
    lifecycle:
      terminationGracePeriodSeconds: integer | default=30
      imagePullPolicy: string | default=IfNotPresent enum="Always,IfNotPresent,Never"

  envOverrides:
    # Environment-overridable parameters
    resources:
      requests:
        cpu: string | default=100m
        memory: string | default=256Mi
      limits:
        cpu: string | default=500m
        memory: string | default=512Mi
    autoscaling:
      enabled: boolean | default=false
      minReplicas: integer | default=1
      maxReplicas: integer | default=10
      targetCPUUtilization: integer | default=80
```

**Example Addon 1: Persistent Volume Claim with Mount** - A PE defined Addon that allows developers to add a persistent volume mount to a Component.

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Addon
metadata:
  name: add-volume-mount
  namespace: default
spec:
  schema:
    parameters: # Developer-facing parameters
      volumeName: string | required=true
      mountPath: string | required=true # Developer decides where in the container to mount the volume
      containerName: string # Which container to mount

    envOverrides: # Platform engineers can override per environment
      size: string | default=10Gi
      storageClass: string | default=standard

  creates:
    - template:
        apiVersion: v1
        kind: PersistentVolumeClaim
        metadata:
          name: ${metadata.name}-${instanceName}
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: ${spec.size}
          storageClassName: ${spec.storageClass}

  patches:
    # Attach PVC as a volume in the pod spec
    - target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: add
          path: /spec/template/spec/volumes/-
          value:
            name: ${spec.volumeName}
            persistentVolumeClaim:
              claimName: ${metadata.name}-${instanceName}

    # Mount the PVC into the developer-specified container at the mountPath
    - target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: add
          path: /spec/template/spec/containers/[?(@.name=='${spec.containerName}')]/volumeMounts/-
          value:
            name: ${spec.volumeName}
            mountPath: ${spec.mountPath}
```

**Example Addon 2: EmptyDir Volume with Sidecar** - Allows legacy applications to stream their file based logs to stdout for log collection.

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Addon
metadata:
  name: add-file-logging-sidecar
  namespace: default
spec:
  displayName: "Stream File Logs to Stdout"
  description: "Pushes logs from a log file to stdout so that logs will be collected by the system"

  schema:
    parameters:
      logFilePath: string | required=true
      containerName: string # Which container to mount to (defaults to app)

  patches:
    - target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        # Inject sidecar container
        - op: add
          path: /spec/template/spec/containers/-
          value:
            name: log-sidecar
            image: busybox
            command: ["/bin/sh", "-c"]
            args:
              - |
                echo "Starting log tail for ${spec.logFilePath}"
                tail -n+1 -F ${spec.logFilePath}
            volumeMounts:
              - name: app-logs
                mountPath: /logs

        # Ensure main container has log volume
        - op: add
          path: /spec/template/spec/containers/[?(@.name=='${spec.containerName}')]/volumeMounts/-
          value:
            name: app-logs
            mountPath: /logs

        # Add volume for log directory (shared between app + sidecar)
        - op: add
          path: /spec/template/spec/volumes/-
          value:
            name: app-logs
            emptyDir: {}
```

### Step 4: Environment-Specific Overrides

- As both `ComponentTypeDefinitions` and `Addons` define `envOverrides` fields, this `ComponentDeployment` resource targeting a particular `Environment` can override the default values that need to be adjusted for a given environment.
- This is a more structured, strongly-typed and validate-able UX for the PE as opposed to using something like Kustomize patches.

**Example: ComponentDeployment for the `production` environment for a component named "checkout-service"**

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ComponentDeployment
metadata:
  name: checkout-service-prod
spec:
  owner:
    componentName: checkout-service
  environment: production

  # Override values in the Component for this environment.
  # These fields are defined in the ComponentTypeDefinition's envOverrides section that instantiated this component.
  overrides:
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 2000m
        memory: 2Gi
    autoscaling:
      enabled: true
      minReplicas: 5
      maxReplicas: 50
      targetCPUUtilization: 70

  # Override addon values for the environment (keyed by instanceName).
  # These fields are defined in the addon's envOverrides section.
  addonOverrides:
    app-data: # instanceName
      size: 200Gi # Much larger in prod
      storageClass: premium
```

### Addon Patch Syntax

Addons apply changes to rendered resources through patch documents that mirror Kustomize’s patch format: each entry selects a resource and runs one or more operations against JSON Pointer–style paths. The standard JSON Patch verbs (`add`, `replace`) are delegated to the upstream `json-patch` engine, while `mergeShallow` is a openchoreo-specific convenience that overlays top-level map keys without replacing sibling values. This balance gives authors familiar semantics with a minimal set of extensions tailored for addon composition.

- **Resource targeting**: Every patch specifies a `target` block. Alongside the resource’s `group/version/kind`, addons can carry an optional CEL-based `where` predicate to limit the patch to specific instances. Paths themselves follow standard JSON Pointer notation.

  ```yaml
  patches:
    - target:
        group: external-secrets.io
        version: v1beta1
        kind: ExternalSecretStore
        where: ${resource.metadata.name.endsWith("-secret-envs")}
      operations:
        - op: add
          path: /spec/refreshInterval
          value: "5m"
  ```

- **List iteration**: The top-level `forEach` field repeats a patch block for every item in a CEL-evaluated list. A companion `var` key is required to name the binding used inside the operations. Array filters (`[?(@.field=='value')]`) are available on every path—not just inside loops—and this example shows the binding selecting the matching container inline.

  ```yaml
  patches:
    - forEach: ${spec.mounts}
      var: mount
      target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: add
          path: /spec/template/spec/containers/[?(@.name=='${mount.containerName}')]/volumeMounts/-
          value:
            name: ${spec.volumeName}
            mountPath: ${mount.mountPath}
            readOnly: ${has(mount.readOnly) ? mount.readOnly : false}
            subPath: ${has(mount.subPath) ? mount.subPath : ""}
  ```

- **Shallow map overlays**: Use `mergeShallow` to add or replace specific keys within metadata maps without re-sending the entire payload.

  ```yaml
  patches:
    - target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: mergeShallow
          path: /spec/template/metadata/annotations
          value:
            custom.annotation/foo: foo
            custom.annotation/bar: bar
  ```

## Deployment Flow and Environment Promotion

OpenChoreo separates **promotable content** from **environment-specific overrides** to enable safe, auditable deployments across environments. This uses ComponentDeployment (introduced earlier) along with **ComponentEnvSnapshot**, a new resource containing full copies of ComponentTypeDefinition, Component, Addons, and Workload.

### How It Works

**Deployment**: When a Component, ComponentTypeDefinition, Addon, or Workload is updated, a ComponentEnvSnapshot is created or updated in the first environment of the deployment pipeline. The snapshot is rendered with that environment's ComponentDeployment to produce a Release containing final Kubernetes manifests. Changes to either the snapshot or ComponentDeployment trigger Release updates.

**Promotion**: Promotion copies the snapshot content to a target environment, where it's rendered with that environment's ComponentDeployment. The same snapshot content produces different Releases based on each environment's settings (e.g., 1 replica in dev, 10 in prod).

**Key Constraint**: Changes are automatically deployed only to the first environment. Other environments remain stable until explicitly promoted.

### Benefits

This separation provides clear boundaries between promotable content and environment-specific configuration, enforces progressive rollout workflows, and ensures identical component definitions across environments with only intentional configuration differences.

### ComponentEnvSnapshot Structure

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ComponentEnvSnapshot
metadata:
  name: checkout-service-dev
spec:
  owner:
    componentName: checkout-service
  environment: production

  # Full embedded copies (not references!)
  componentTypeDefinition:
    apiVersion: openchoreo.dev/v1alpha1
    kind: ComponentTypeDefinition
    metadata:
      name: web-app
      namespace: default
    spec:
      workloadType: deployment
      schema: { ... }
      resources: { ... }

  component:
    apiVersion: openchoreo.dev/v1alpha1
    kind: Component
    metadata:
      name: checkout-service
    spec:
      componentType:
        kind: ComponentType
        name: deployment/web-app
      parameters: { ... }
      addons:
        - name: persistent-volume-claim
          instanceName: app-data
          config: { ... }

  addons:
    - apiVersion: openchoreo.dev/v1alpha1
      kind: Addon
      metadata:
        name: persistent-volume-claim
        namespace: default
      spec:
        creates: [...]
        patches: [...]

  workload:
    apiVersion: openchoreo.dev/v1alpha1
    kind: Workload
    metadata:
      name: checkout-service
    spec:
      image: gcr.io/project/checkout-service:v1.2.3
      endpoints: [...]
      connections: [...]
```



File: docs/proposals/README.md
---
# OpenChoreo Proposals

This directory contains design proposals for OpenChoreo. Proposals are used to document significant changes to the platform before implementation.

## When to Write a Proposal

A proposal is required for:
- New CRDs or significant changes to existing CRDs
- Major architectural changes
- Breaking changes to APIs or behavior
- New features that impact multiple components
- Changes affecting the developer experience

## Proposal Process

### 1. Create a GitHub Issue
First, create a GitHub issue describing the problem or enhancement you want to address. This issue will be assigned a number that becomes the proposal identifier.

### 2. Open a Discussion
After creating the issue, open a [GitHub Discussion under the "Proposals" category](https://github.com/openchoreo/openchoreo/discussions/categories/proposals) to:
- Present your initial design ideas
- Gather feedback from the community
- Iterate on the design based on input
- Build consensus before formal documentation

### 3. Write the Proposal
Once the discussion reaches consensus:
1. Copy the `xxxx-proposal-template.md` file
2. Rename it to `<issue-number>-<descriptive-title>.md` where:
   - `<issue-number>` is zero-padded to 4 digits (e.g., 0245)
   - `<descriptive-title>` uses kebab-case (e.g., introduce-build-plane)
   - Example: `0245-introduce-build-plane.md`
3. If your proposal includes diagrams or images:
   - Create a directory `<issue-number>-assets/` (e.g., `0245-assets/`)
   - Place all images, diagrams, and other assets in this directory
   - Reference them from your proposal using relative paths (e.g., `![Architecture](0245-assets/architecture.png)`)
4. Fill out all sections of the template
5. Reference both the GitHub issue and discussion if applicable

### 4. Submit via Pull Request
1. Create a PR with your proposal file
2. Link the PR to the original GitHub issue and discussion
3. Request reviews from relevant maintainers

### 5. Proposal Status Lifecycle
Once merged into the repository, proposals have these statuses:
- **Approved**: Proposal accepted, implementation can begin
- **Rejected**: Proposal was not accepted (kept with rejection reasoning documented)

Note: Both approved and rejected proposals remain in the repository for historical reference and to document decision rationale.

## Improving the Proposal Process

Have suggestions to improve the proposal process itself? Please open a GitHub Discussion to share your ideas and gather feedback from the community.



File: docs/proposals/xxxx-proposal-template.md
---
# Title

**Authors**:  
_@your-github-handle_

**Reviewers**:  
_@github-handle (assigned reviewers)_

**Created Date**:  
_YYYY-MM-DD_

**Status**:  
_Submitted / Accepted / Rejected / Implemented_

**Related Issues/PRs**:  
_Linked GitHub issues or pull requests_

---

## Summary

_A high-level overview of the proposal. Focus on the what and why._

---

## Motivation

_Explain the problem this proposal is solving. Why is this feature necessary? What value does it add to OpenChoreo or its users?_

---

## Goals

_What this proposal aims to achieve._

---

## Non-Goals

_What this proposal does **not** aim to solve (to set scope clearly)._

---

## Impact

_Describe which areas of the OpenChoreo system will be affected (e.g., API Server, Controllers, CLI, SDKs). Include any considerations around backward compatibility, migration, or operational changes._

---


## Design

_Elaborate on the technical design of the feature. This may include component-level architecture, state transitions, interface definitions, configurations, and error handling strategies. Add diagrams or flowcharts as needed to communicate the design clearly._

---

## Appendix (optional)

_Any extra context, links to discussions, references, etc._



File: docs/resource-kind-reference-guide.md
---
# OpenChoreo Resource Kinds

This document describes the resource kinds used in OpenChoreo CRDs, the relationships between them, and detailed information about each kind.

## Overview

- [Design Considerations](#design-considerations)
- [Resource Hierarchy](#resource-hierarchy)
- [Kubernetes Metadata Representation](#kubernetes-metadata-representation)
- [Resource Kinds](#resource-kinds)
  - [Developer Abstractions](#developer-abstractions)
    - [Project](#project)
    - [Component](#component)
    - [Workload](#workload)
    - [ComponentRelease](#componentrelease)
    - [ReleaseBinding](#releasebinding)
    - [RenderedRelease](#renderedrelease)
  - [Composition and Templating](#composition-and-templating)
    - [ComponentType / ClusterComponentType](#componenttype--clustercomponenttype)
    - [Trait / ClusterTrait](#trait--clustertrait)
    - [Workflow / ClusterWorkflow](#workflow--clusterworkflow)
    - [WorkflowRun](#workflowrun)
  - [Platform Infrastructure](#platform-infrastructure)
    - [DeploymentPipeline](#deploymentpipeline)
    - [Environment](#environment)
    - [DataPlane / ClusterDataPlane](#dataplane--clusterdataplane)
    - [WorkflowPlane / ClusterWorkflowPlane](#workflowplane--clusterworkflowplane)
    - [ObservabilityPlane / ClusterObservabilityPlane](#observabilityplane--clusterobservabilityplane)
  - [External Configuration](#external-configuration)
    - [SecretReference](#secretreference)
  - [Authorization](#authorization)
    - [AuthzRole / ClusterAuthzRole](#authzrole--clusterauthzrole)
    - [AuthzRoleBinding / ClusterAuthzRoleBinding](#authzrolebinding--clusterauthzrolebinding)
  - [Observability Alerts](#observability-alerts)
    - [ObservabilityAlertRule](#observabilityalertrule)
    - [ObservabilityAlertsNotificationChannel](#observabilityalertsnotificationchannel)

## Design Considerations

When designing the resource kinds for OpenChoreo, several principles have been followed to ensure consistency between resource kinds. These considerations help to keep a clear mapping of OpenChoreo concepts to resource kinds while maintaining simplicity.

- Each concept in OpenChoreo has a corresponding resource kind. This one-to-one mapping ensures that users can easily understand the resource model.
- In situations where a resource kind is required but does not directly correspond to a core concept:
  - If two resource kinds share a one-to-one relationship, they are combined into a single resource kind.
  - If combining them introduces implementation complexity or if it makes logical sense to keep them distinct, they remain separate.
- **Scope pairing**: Most resources have namespace-scoped and cluster-scoped variants (e.g., `ComponentType` / `ClusterComponentType`). Cluster-scoped types can only reference other cluster-scoped types.
- **Immutability**: Key fields use `XValidation:rule="self == oldSelf"` to enforce immutability after creation (e.g., ComponentRelease spec, Component owner).
- **CEL templating**: Resource templates, trait creates/patches, and workflow templates use `${...}` syntax for CEL expressions.

[Back to Top](#overview)

## Resource Hierarchy

The following diagram shows the relationships between the core resource kinds in OpenChoreo.

```mermaid
erDiagram
    Project ||--o{ Component : "contains"
    Component ||--|| Workload : "has"
    Component }o--|| ComponentType : "references"
    Component ||--o{ ComponentRelease : "creates"
    ComponentRelease ||--o{ ReleaseBinding : "bound to"
    ReleaseBinding ||--o{ RenderedRelease : "renders"
    ReleaseBinding }o--|| Environment : "targets"
    Environment }o--|| DataPlane : "references"
    Project }o--|| DeploymentPipeline : "references"
    DeploymentPipeline }o--o{ Environment : "defines promotion paths"
    ComponentType }o--o{ Trait : "embeds/allows"
    Component }o--o{ Trait : "attaches"
    Component }o--o| Workflow : "references"
```

### Core Deployment Flow

```
Project (defines deployment pipeline)
  └── Component (references ComponentType, attaches Traits, configures Workflow)
       ├── Workload (container spec, endpoints, dependencies)
       └── ComponentRelease (immutable snapshot of ComponentType + Traits + Workload)
            └── ReleaseBinding (binds release to Environment with overrides)
                 └── RenderedRelease (final K8s manifests → applied to DataPlane)
```

### Platform Infrastructure

```
DeploymentPipeline (defines promotion paths between Environments)
Environment (runtime context: dev/staging/prod, references DataPlane)
DataPlane / ClusterDataPlane (target K8s cluster, agent-based connectivity)
WorkflowPlane / ClusterWorkflowPlane (Argo-based CI/CD execution)
ObservabilityPlane / ClusterObservabilityPlane (OpenSearch-based monitoring)
```

[Back to Top](#overview)

## Kubernetes Metadata Representation

OpenChoreo resources use standard Kubernetes metadata conventions:

| Field | Description |
|-------|-------------|
| `metadata.name` | Unique name within scope (namespace or cluster) |
| `metadata.namespace` | Namespace for namespace-scoped resources |
| `metadata.labels` | Kubernetes labels for selection and filtering |
| `metadata.annotations` | Additional metadata |

Resources are organized under Kubernetes namespaces which serve as organizational boundaries (similar to organizations/tenants). Projects, Components, and their related resources all live within a namespace.

[Back to Top](#overview)

## Resource Kinds

### Developer Abstractions

---

#### Project

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Logical grouping of related components and definition of deployment progression |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deploymentPipelineRef` | DeploymentPipelineRef | Yes | References the DeploymentPipeline that defines environments and promotion paths |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `observedGeneration` | int64 | Last observed generation |
| `conditions` | []Condition | Standard Kubernetes conditions |

**Relationships:**
- References: DeploymentPipeline
- Owns: Components, ReleaseBindings

[Back to Top](#overview)

---

#### Component

| | |
|---|---|
| **Scope** | Namespaced |
| **Short Names** | `comp`, `comps` |
| **Purpose** | Developer's deployable unit — the primary resource developers interact with |

**Spec:**

| Field | Type | Required | Mutable | Description |
|-------|------|----------|---------|-------------|
| `owner.projectName` | string | Yes | No | Parent Project name |
| `componentType` | ComponentTypeRef | Yes | No | References ComponentType in format `{workloadType}/{name}` |
| `autoDeploy` | bool | No | Yes | Auto-create ComponentRelease and ReleaseBinding on changes |
| `autoBuild` | bool | No | Yes | Trigger builds on code push (requires webhooks) |
| `parameters` | RawExtension | No | Yes | Developer-provided values matching ComponentType schema |
| `traits[]` | ComponentTrait[] | No | Yes | Additional trait instances (instanceName, kind, name, parameters) |
| `workflow` | ComponentWorkflowConfig | No | Yes | Build workflow reference (kind, name, parameters) |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `observedGeneration` | int64 | Last observed generation |
| `conditions` | []Condition | Standard Kubernetes conditions |
| `latestRelease` | LatestRelease | Name and hash of the latest ComponentRelease |

**Relationships:**
- Owner: Project (via `spec.owner.projectName`)
- References: ComponentType or ClusterComponentType, Trait/ClusterTrait, Workflow/ClusterWorkflow
- Creates: ComponentRelease (when `autoDeploy=true`)
- Has: Workload (one-to-one, same namespace)

[Back to Top](#overview)

---

#### Workload

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Container specification, endpoints, connections, and source configuration for a component |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner.projectName` | string | Yes | Parent Project (immutable) |
| `owner.componentName` | string | Yes | Parent Component (immutable) |
| `container.image` | string | Yes | OCI container image |
| `container.command` | []string | No | Container entrypoint |
| `container.args` | []string | No | Container arguments |
| `container.env[]` | EnvVar[] | No | Environment variables (key/value or secretKeyRef) |
| `container.files[]` | FileVar[] | No | Mounted files (key/mountPath/value or secretKeyRef) |
| `endpoints` | map[string]WorkloadEndpoint | No | Named endpoints with type, port, visibility, basePath |
| `dependencies.endpoints[]` | WorkloadConnection[] | No | Dependencies on other components' endpoints |

**Endpoint Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | EndpointType | Yes | HTTP, gRPC, GraphQL, Websocket, TCP, UDP |
| `port` | int32 | Yes | Exposed port |
| `targetPort` | int32 | No | Container listening port (defaults to port) |
| `visibility` | []EndpointVisibility | No | project, namespace, internal, external |
| `basePath` | string | No | URL base path |
| `schema` | EndpointSchema | No | API schema (type + content) |

**Relationships:**
- Owner: Component (via `spec.owner.componentName`)
- Referenced by: ComponentRelease (snapshot copy)

[Back to Top](#overview)

---

#### ComponentRelease

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Immutable snapshot created when a component is released, capturing frozen specs |

All spec fields are **immutable** after creation (enforced via `XValidation:rule="self == oldSelf"`).

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner.projectName` | string | Yes | Parent Project |
| `owner.componentName` | string | Yes | Parent Component |
| `componentType` | ComponentReleaseComponentType | Yes | Frozen ComponentType kind, name, and full spec |
| `traits[]` | ComponentReleaseTrait[] | No | Frozen Trait kind, name, and full spec |
| `componentProfile` | ComponentProfile | No | Frozen parameters and trait configurations |
| `workload` | WorkloadTemplateSpec | Yes | Frozen workload (container, endpoints) |

**Relationships:**
- Owner: Component
- Referenced by: ReleaseBinding (via `spec.releaseName`)
- Contains frozen copies of: ComponentType spec, Trait specs, Workload spec

[Back to Top](#overview)

---

#### ReleaseBinding

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Binds a ComponentRelease to an Environment with environment-specific overrides |

**Spec:**

| Field | Type | Required | Mutable | Description |
|-------|------|----------|---------|-------------|
| `owner.projectName` | string | Yes | No | Parent Project |
| `owner.componentName` | string | Yes | No | Parent Component |
| `environment` | string | Yes | No | Target environment name |
| `releaseName` | string | No | Yes | ComponentRelease to deploy |
| `componentTypeEnvironmentConfigs` | RawExtension | No | Yes | Per-environment ComponentType overrides |
| `traitEnvironmentConfigs` | map[string]RawExtension | No | Yes | Per-environment trait overrides (keyed by instanceName) |
| `workloadOverrides` | WorkloadOverrideTemplateSpec | No | Yes | Container env/file overrides |
| `state` | ReleaseState | No | Yes | Active (default) or Undeploy |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `observedGeneration` | int64 | Last observed generation |
| `conditions` | []Condition | Standard Kubernetes conditions |
| `endpoints[]` | EndpointURLStatus[] | Resolved invoke URLs (service URL, gateway URLs) |
| `resolvedConnections[]` | ResolvedConnection[] | Successfully resolved inter-component connections |
| `pendingConnections[]` | PendingConnection[] | Connections awaiting resolution |
| `secretReferenceNames[]` | []string | SecretReferences used by workload |

**Relationships:**
- Owner: Project (via `spec.owner.projectName`)
- References: ComponentRelease, Environment
- Creates: RenderedRelease (rendered K8s manifests)

[Back to Top](#overview)

---

#### RenderedRelease

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Final rendered K8s manifests deployed to a data plane or observability plane |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner.projectName` | string | Yes | Parent Project |
| `owner.componentName` | string | Yes | Parent Component |
| `environmentName` | string | Yes | Target environment |
| `resources[]` | Resource[] | No | Rendered K8s resources (id + raw object) |
| `targetPlane` | string | No | `dataplane` (default) or `observabilityplane` |
| `interval` | Duration | No | Stable-state watch interval (default 5m) |
| `progressingInterval` | Duration | No | Transitioning watch interval (default 10s) |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | []Condition | Standard Kubernetes conditions |
| `resources[]` | ResourceStatus[] | Per-resource status with health tracking |

**Resource Health States:** Unknown, Progressing, Healthy, Suspended, Degraded

**Relationships:**
- Created by: ReleaseBinding controller
- Deployed to: DataPlane or ObservabilityPlane

For detailed design documentation, see [RenderedRelease CRD Design](crds/renderedrelease.md).

[Back to Top](#overview)

---

### Composition and Templating

---

#### ComponentType / ClusterComponentType

| | |
|---|---|
| **Scope** | Namespaced (`ComponentType`) / Cluster (`ClusterComponentType`) |
| **Short Names** | `ct`, `cts` |
| **Purpose** | Platform engineer's template defining what a component looks like and what resources it creates |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workloadType` | string | Yes | Immutable. One of: deployment, statefulset, cronjob, job, proxy |
| `parameters` | SchemaSection | No | Developer-configurable fields (ocSchema or openAPIV3Schema) |
| `environmentConfigs` | SchemaSection | No | Per-environment override schema |
| `traits[]` | ComponentTypeTrait[] | No | Pre-configured embedded traits with parameter/environmentConfig bindings |
| `allowedTraits[]` | TraitRef[] | No | Additional traits developers can attach |
| `allowedWorkflows[]` | WorkflowRef[] | No | Permitted build workflows |
| `validations[]` | ValidationRule[] | No | CEL validation rules |
| `resources[]` | ResourceTemplate[] | Yes (min 1) | K8s resource templates with CEL expressions |

**ResourceTemplate Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Resource identifier (must match workloadType for primary resource) |
| `targetPlane` | string | No | `dataplane` (default) or `observabilityplane` |
| `includeWhen` | string | No | CEL expression — conditionally include resource |
| `forEach` | string | No | CEL expression — iterate to create multiple resources |
| `var` | string | No | Loop variable name |
| `template` | RawExtension | Yes | K8s resource with `${...}` CEL template expressions |

**SchemaSection** supports two mutually exclusive formats:
- `ocSchema` — OpenChoreo shorthand format (e.g., `replicas: "integer | default=1"`)
- `openAPIV3Schema` — Standard OpenAPI v3 JSON Schema

**Cluster-scoped variant** (`ClusterComponentType`) only references `ClusterTrait` and `ClusterWorkflow`.

[Back to Top](#overview)

---

#### Trait / ClusterTrait

| | |
|---|---|
| **Scope** | Namespaced (`Trait`) / Cluster (`ClusterTrait`) |
| **Purpose** | Composable behavior that can be added to components — creates new resources or patches existing ones |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parameters` | SchemaSection | No | Developer-facing configuration schema |
| `environmentConfigs` | SchemaSection | No | Per-environment override schema |
| `validations[]` | ValidationRule[] | No | CEL validation rules |
| `creates[]` | TraitCreate[] | No | New K8s resources to create |
| `patches[]` | TraitPatch[] | No | JSONPatch modifications to existing resources |

**TraitCreate** has the same structure as ResourceTemplate (id, targetPlane, includeWhen, forEach, var, template).

**TraitPatch Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | PatchTarget | Yes | Target resource by group/version/kind, optional `where` CEL filter |
| `targetPlane` | string | No | `dataplane` (default) or `observabilityplane` |
| `forEach` | string | No | CEL expression for iteration |
| `operations[]` | JSONPatchOperation[] | Yes (min 1) | JSONPatch operations (op: add/replace/remove, path, value) |

[Back to Top](#overview)

---

#### Workflow / ClusterWorkflow

| | |
|---|---|
| **Scope** | Namespaced (`Workflow`) / Cluster (`ClusterWorkflow`) |
| **Purpose** | Build workflow template defining how source code is built into container images |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflowPlaneRef` | WorkflowPlaneRef | No | Target WorkflowPlane (default: ClusterWorkflowPlane/default) |
| `parameters` | SchemaSection | No | Developer-configurable build parameters |
| `runTemplate` | RawExtension | Yes | K8s resource template (typically Argo WorkflowTemplate) |
| `resources[]` | WorkflowResource[] | No | Additional resources deployed alongside (secrets, configmaps) |
| `externalRefs[]` | ExternalRef[] | No | External CR references resolved at runtime |
| `ttlAfterCompletion` | string | No | TTL for cleanup (e.g., `90d`, `1h30m`) |

**Cluster-scoped variant** (`ClusterWorkflow`) only references `ClusterWorkflowPlane`.

[Back to Top](#overview)

---

#### WorkflowRun

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Runtime execution instance of a Workflow |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflow.kind` | string | Yes | WorkflowRefKind (immutable, default: ClusterWorkflow) |
| `workflow.name` | string | Yes | Workflow/ClusterWorkflow name (immutable) |
| `workflow.parameters` | RawExtension | No | Developer-provided build parameter values |
| `ttlAfterCompletion` | string | No | Copied from Workflow template |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | []Condition | Standard Kubernetes conditions |
| `runReference` | ResourceReference | Actual workflow execution reference in the workflow plane cluster |
| `resources[]` | ResourceReference[] | Additional resources applied |
| `tasks[]` | WorkflowTask[] | Vendor-neutral task view (name, phase, timing, message) |
| `startedAt` | Time | Execution start time |
| `completedAt` | Time | Execution completion time |

**Task Phases:** Pending, Running, Succeeded, Failed, Skipped, Error

[Back to Top](#overview)

---

### Platform Infrastructure

---

#### DeploymentPipeline

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Defines promotion paths between environments |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `promotionPaths[]` | PromotionPath[] | No | List of source → target environment promotion paths |
| `promotionPaths[].sourceEnvironmentRef` | EnvironmentRef | Yes | Source environment |
| `promotionPaths[].targetEnvironmentRefs[]` | TargetEnvironmentRef[] | Yes | Destination environments |

**Relationships:**
- Referenced by: Project
- References: Environment

[Back to Top](#overview)

---

#### Environment

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Runtime context (dev, staging, prod) for component deployment |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataPlaneRef` | DataPlaneRef | No | Target DataPlane (default: DataPlane/default). Immutable once set. |
| `isProduction` | bool | No | Marks environment as production |
| `gateway` | GatewaySpec | No | Environment-specific gateway configuration (overrides DataPlane gateway) |

**Gateway Configuration:**

```yaml
gateway:
  ingress:
    external:
      name: "gateway-name"
      namespace: "gateway-namespace"
      http:
        listenerName: "http"
        port: 8080
        host: "app.example.com"
      https:
        listenerName: "https"
        port: 8443
        host: "app.example.com"
    internal:
      # Same structure as external
  egress:
    # Same structure as ingress
```

**Relationships:**
- Referenced by: ReleaseBinding, DeploymentPipeline
- References: DataPlane or ClusterDataPlane

[Back to Top](#overview)

---

#### DataPlane / ClusterDataPlane

| | |
|---|---|
| **Scope** | Namespaced (`DataPlane`) / Cluster (`ClusterDataPlane`) |
| **Purpose** | Target Kubernetes cluster for workload deployment, connected via cluster agent |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `planeID` | string | No* | Logical plane identifier (*required for ClusterDataPlane) |
| `clusterAgent` | ClusterAgentConfig | Yes | WebSocket connection config with client CA |
| `gateway` | GatewaySpec | No | API gateway configuration |
| `secretStoreRef` | SecretStoreRef | No | ESO ClusterSecretStore reference |
| `observabilityPlaneRef` | ObservabilityPlaneRef | No | Associated observability plane |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | []Condition | Standard Kubernetes conditions |
| `agentConnection` | AgentConnectionStatus | Connection state (connected, agent count, heartbeat times) |

**Cluster-scoped variant** (`ClusterDataPlane`) only references `ClusterObservabilityPlane`.

[Back to Top](#overview)

---

#### WorkflowPlane / ClusterWorkflowPlane

| | |
|---|---|
| **Scope** | Namespaced (`WorkflowPlane`) / Cluster (`ClusterWorkflowPlane`) |
| **Purpose** | Argo-based CI/CD execution environment |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `planeID` | string | No* | Logical plane identifier (*required for cluster-scoped) |
| `clusterAgent` | ClusterAgentConfig | Yes | WebSocket connection config |
| `secretStoreRef` | SecretStoreRef | No | ESO ClusterSecretStore reference |
| `observabilityPlaneRef` | ObservabilityPlaneRef | No | Associated observability plane |

**Status:** Same as DataPlane (conditions + agentConnection).

[Back to Top](#overview)

---

#### ObservabilityPlane / ClusterObservabilityPlane

| | |
|---|---|
| **Scope** | Namespaced (`ObservabilityPlane`) / Cluster (`ClusterObservabilityPlane`) |
| **Purpose** | OpenSearch-based monitoring and observability |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `planeID` | string | No* | Logical plane identifier (*required for cluster-scoped) |
| `clusterAgent` | ClusterAgentConfig | Yes | WebSocket connection config |
| `observerURL` | string | Yes | Base URL of the Observer API |
| `rcaAgentURL` | string | No | RCA Agent API URL |

**Status:** Same as DataPlane (conditions + agentConnection).

[Back to Top](#overview)

---

### External Configuration

---

#### SecretReference

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Maps external secrets to Kubernetes Secrets via External Secrets Operator |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template` | SecretTemplate | Yes | Secret type and metadata (annotations, labels) |
| `data[]` | SecretDataSource[] | Yes (min 1) | Mapping of secret keys to external store references |
| `refreshInterval` | Duration | No | Refresh interval (default: 1h) |

**SecretDataSource Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `secretKey` | string | Yes | Kubernetes secret key name |
| `remoteRef.key` | string | Yes | Path in external secret store |
| `remoteRef.property` | string | No | Specific field within the secret |
| `remoteRef.version` | string | No | Version identifier |

**Status:**

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | []Condition | Standard Kubernetes conditions |
| `lastRefreshTime` | Time | Last successful refresh |
| `secretStores[]` | SecretStoreReference[] | Associated secret stores |

[Back to Top](#overview)

---

### Authorization

---

#### AuthzRole / ClusterAuthzRole

| | |
|---|---|
| **Scope** | Namespaced (`AuthzRole`) / Cluster (`ClusterAuthzRole`) |
| **Purpose** | Defines a set of permitted actions |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actions[]` | []string | Yes (min 1) | Allowed actions (e.g., `component:create`, `component:delete`) |
| `description` | string | No | Human-readable description |

[Back to Top](#overview)

---

#### AuthzRoleBinding / ClusterAuthzRoleBinding

| | |
|---|---|
| **Scope** | Namespaced (`AuthzRoleBinding`) / Cluster (`ClusterAuthzRoleBinding`) |
| **Purpose** | Grants roles to JWT-authenticated subjects |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entitlement` | EntitlementClaim | Yes | JWT claim/value pair identifying the subject |
| `roleMappings[]` | RoleMapping[] | Yes (min 1) | Role references with optional scope |
| `effect` | EffectType | No | `allow` (default) or `deny` |

**RoleMapping Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `roleRef` | RoleRef | Yes | References AuthzRole or ClusterAuthzRole (kind + name) |
| `scope` | TargetScope | No | Optional narrowing to project and/or component |

**Scope Constraints:**
- Namespace-scoped: `scope` can specify `project` and optionally `component` (component requires project)
- Cluster-scoped: `scope` can additionally specify `namespace` (project requires namespace, component requires project)

[Back to Top](#overview)

---

### Observability Alerts

---

#### ObservabilityAlertRule

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Defines alert rules based on log or metric telemetry data |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | ObservabilityAlertSource | Yes | Telemetry source (type: log or metric, query, timeWindow) |
| `condition` | ObservabilityAlertCondition | Yes | Trigger condition (operator: gt/lt/gte/lte/eq, threshold) |
| `severity` | ObservabilityAlertSeverity | Yes | info, warning, or critical |
| `notificationChannelRef` | NotificationChannelRef | No | Reference to notification channel |

---

#### ObservabilityAlertsNotificationChannel

| | |
|---|---|
| **Scope** | Namespaced |
| **Purpose** | Defines notification channels (email, webhook) for alert delivery |

**Spec:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | NotificationChannelType | Yes | `email` or `webhook` |
| `email` | EmailConfig | Conditional | Email configuration (from, to, SMTP, template) — required when type=email |
| `webhook` | WebhookConfig | Conditional | Webhook configuration (URL, headers, template) — required when type=webhook |

[Back to Top](#overview)

---

## Common Reference Types

OpenChoreo uses typed reference types to link resources together. Each reference type includes a `kind` field that determines whether the target is namespace-scoped or cluster-scoped.

| Reference Type | Kind Values | Default Kind |
|----------------|-------------|--------------|
| `ComponentTypeRef` | ComponentType, ClusterComponentType | ComponentType |
| `TraitRef` | Trait, ClusterTrait | Trait |
| `WorkflowRef` | Workflow, ClusterWorkflow | ClusterWorkflow |
| `DataPlaneRef` | DataPlane, ClusterDataPlane | DataPlane |
| `WorkflowPlaneRef` | WorkflowPlane, ClusterWorkflowPlane | ClusterWorkflowPlane |
| `ObservabilityPlaneRef` | ObservabilityPlane, ClusterObservabilityPlane | ObservabilityPlane |
| `RoleRef` | AuthzRole, ClusterAuthzRole | AuthzRole |
| `DeploymentPipelineRef` | DeploymentPipeline | DeploymentPipeline |
| `EnvironmentRef` | Environment | Environment |

ComponentTypeRef uses a special name format: `{workloadType}/{componentTypeName}` (e.g., `deployment/my-service-type`).

[Back to Top](#overview)



File: docs/templating/configuration_helpers.md
---
# Configuration Helpers

This document provides detailed documentation for all configuration helper methods available in the templating context. These helpers simplify working with container configurations, environment variables, and file mounts.

## Overview

Configuration helpers are CEL extension functions that provide convenient methods to work with the `configurations` object in your templates. They help reduce boilerplate code and make templates more readable and maintainable.

## Helper Methods

### Environment Variable Helpers

#### configurations.toContainerEnvFrom()

Helper method that generates an `envFrom` array for the container configuration. This simplifies the creation of `configMapRef` and `secretRef` entries based on what environment variables are available.

**Parameters:** None

**Returns:** List of envFrom entries, each containing either:

| Field | Type | Description |
|-------|------|-------------|
| `configMapRef` | map | Reference to ConfigMap (only present if container has config envs) |
| `secretRef` | map | Reference to Secret (only present if container has secret envs) |

**Example usage:**

```yaml
# Simple envFrom generation using the helper
spec:
  template:
    spec:
      containers:
        - name: main
          image: myapp:latest
          envFrom: ${configurations.toContainerEnvFrom()}

# Before - verbose manual logic:
envFrom: |
  ${(has(configurations.configs.envs) && configurations.configs.envs.size() > 0 ?
    [{
      "configMapRef": {
        "name": oc_generate_name(metadata.name, "env-configs")
      }
    }] : []) +
  (has(configurations.secrets.envs) && configurations.secrets.envs.size() > 0 ?
    [{
      "secretRef": {
        "name": oc_generate_name(metadata.name, "env-secrets")
      }
    }] : [])}

# After - clean helper usage:
envFrom: ${configurations.toContainerEnvFrom()}
```

**Combining with additional entries:**

```yaml
# Can be combined with CEL operations
envFrom: |
  ${configurations.toContainerEnvFrom() +
    [{"configMapRef": {"name": "additional-config"}}]}
```

#### configurations.toConfigEnvsByContainer()

Helper method that generates a list of objects for creating ConfigMaps from environment variables. Each object contains the generated resource name and the list of environment variables for the container. This is useful for `forEach` iteration when creating ConfigMaps for the container's config envs.

**Parameters:** None

**Returns:** List of objects, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `resourceName` | string | Generated ConfigMap name (componentName-environmentName-env-configs-hash) |
| `envs` | array | List of environment variable objects with `name` and `value` |

**Example usage:**

```yaml
# Generate ConfigMaps for the container's config envs
- id: env-config
  forEach: ${configurations.toConfigEnvsByContainer()}
  var: envConfig
  template:
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: ${envConfig.resourceName}
      namespace: ${metadata.namespace}
    data: |
      ${envConfig.envs.transformMapEntry(index, env, {env.name: env.value})}

# Before - verbose manual logic:
forEach: |
  ${has(configurations.configs.envs) && configurations.configs.envs.size() > 0 ?
    [{
      "resourceName": oc_generate_name(metadata.name, "env-configs"),
      "envs": configurations.configs.envs
    }] : []}

# After - clean helper usage:
forEach: ${configurations.toConfigEnvsByContainer()}
```

**Notes:**
- Only returns an entry if the container has config environment variables
- Returns empty list if there are no config envs or only secret envs
- Generated resource names follow the format: `componentName-environmentName-env-configs-hash`

#### configurations.toSecretEnvsByContainer()

Helper method that generates a list of objects for creating ExternalSecrets from secret environment variables. Each object contains the generated resource name and the list of secret environment variables for the container. This is useful for `forEach` iteration when creating ExternalSecrets for the container's secret envs.

The resource names are automatically generated using `metadata.componentName + "-" + metadata.environmentName` as the prefix.

**Parameters:** None

**Returns:** List of objects, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `resourceName` | string | Generated ExternalSecret name (componentName-environmentName-env-secrets-hash) |
| `envs` | array | List of secret environment variable objects with `name` and `remoteRef` |

**Example usage:**

```yaml
# Generate ExternalSecrets for the container's secret envs
- id: secret-env-external
  forEach: ${configurations.toSecretEnvsByContainer()}
  var: secretEnv
  template:
    apiVersion: external-secrets.io/v1
    kind: ExternalSecret
    metadata:
      name: ${secretEnv.resourceName}
      namespace: ${metadata.namespace}
    spec:
      refreshInterval: 15s
      secretStoreRef:
        name: ${dataplane.secretStore}
        kind: ClusterSecretStore
      target:
        name: ${secretEnv.resourceName}
        creationPolicy: Owner
      data: |
        ${secretEnv.envs.map(secret, {
          "secretKey": secret.name,
          "remoteRef": {
            "key": secret.remoteRef.key,
            "property": has(secret.remoteRef.property) ? secret.remoteRef.property : oc_omit()
          }
        })}

# Before - verbose manual logic:
forEach: |
  ${has(configurations.secrets.envs) && configurations.secrets.envs.size() > 0 ?
    [{
      "resourceName": oc_generate_name(metadata.name, "env-secrets"),
      "envs": configurations.secrets.envs
    }] : []}

# After - clean helper usage:
forEach: ${configurations.toSecretEnvsByContainer()}
```

**Notes:**
- Only returns an entry if the container has secret environment variables
- Returns empty list if there are no secret envs or only config envs
- Generated resource names follow the format: `componentName-environmentName-env-secrets-hash`

### File Configuration Helpers

#### configurations.toConfigFileList()

Helper method that extracts `configs.files` from the `configurations` object into a list, useful for `forEach` iteration. This provides config files from the workload container.

**Parameters:** None

**Returns:** List of maps, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name |
| `mountPath` | string | Mount path |
| `value` | string | File content (empty string if using remoteRef) |
| `resourceName` | string | Generated Kubernetes-compliant resource name (componentName-environmentName-config-fileName) |
| `remoteRef` | map | Remote reference (only present if the file uses a secret reference) |

**Example usage:**

```yaml
# Generate a ConfigMap for each config file
resources:
  - id: file-configs
    forEach: ${configurations.toConfigFileList()}
    var: config
    template:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${config.resourceName}
        namespace: ${metadata.namespace}
      data:
        ${config.name}: |
          ${config.value}
```

**Equivalent CEL expression:**

If you need additional fields (e.g., `container` name) or different behavior, use the underlying data directly:

```yaml
forEach: |
  ${configurations.transformList(containerName, cfg,
    cfg.configs.files.map(f, oc_merge(f, {
      "container": containerName,
      "resourceName": oc_generate_name(metadata.name, containerName, "config", f.name.replace(".", "-"))
    }))
  ).flatten()}
```

#### configurations.toSecretFileList()

Helper method that extracts `secrets.files` from the `configurations` object into a list, useful for `forEach` iteration. This provides secret files from the workload container.

The resource names are automatically generated using `metadata.componentName + "-" + metadata.environmentName` as the prefix.

**Parameters:** None

**Returns:** List of maps, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name |
| `mountPath` | string | Mount path |
| `value` | string | File content (empty string if using remoteRef) |
| `resourceName` | string | Generated Kubernetes-compliant resource name (componentName-environmentName-secret-fileName) |
| `remoteRef` | map | Remote reference (only present if the file uses a secret reference) |

**Example usage:**

```yaml
# Generate an ExternalSecret for each secret file
resources:
  - id: file-secrets
    forEach: ${configurations.toSecretFileList()}
    var: secret
    includeWhen: ${has(secret.remoteRef)}
    template:
      apiVersion: external-secrets.io/v1beta1
      kind: ExternalSecret
      metadata:
        name: ${secret.resourceName}
        namespace: ${metadata.namespace}
      spec:
        secretStoreRef:
          name: ${dataplane.secretStore}
          kind: ClusterSecretStore
        target:
          name: ${secret.resourceName}
          creationPolicy: Owner
        data:
          - secretKey: ${secret.name}
            remoteRef:
              key: ${secret.remoteRef.key}
              property: ${secret.remoteRef.property}

  # Generate a Secret for files with inline values
  - id: inline-file-secrets
    forEach: ${configurations.toSecretFileList()}
    var: secret
    includeWhen: ${!has(secret.remoteRef) && secret.value != ""}
    template:
      apiVersion: v1
      kind: Secret
      metadata:
        name: ${secret.resourceName}
        namespace: ${metadata.namespace}
      data:
        ${secret.name}: ${base64.encode(secret.value)}
```

**Equivalent CEL expression:**

If you need additional fields (e.g., `container` name) or different behavior, use the underlying data directly:

```yaml
forEach: |
  ${configurations.transformList(containerName, cfg,
    cfg.secrets.files.map(f, oc_merge(f, {
      "container": containerName,
      "resourceName": oc_generate_name(metadata.name, containerName, "secret", f.name.replace(".", "-"))
    }))
  ).flatten()}
```

### Volume Mount Helpers

#### configurations.toContainerVolumeMounts()

Helper method that generates a `volumeMounts` array for the default container configuration. This simplifies the creation of volume mount entries based on the container's config and secret files. The helper automatically selects the `"default"` container from configurations.

**Parameters:** None

**Returns:** List of volumeMount entries, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Volume name (file-mount-hash format) |
| `mountPath` | string | Full mount path (mountPath + "/" + filename) |
| `subPath` | string | Filename to mount as subPath |

**Example usage:**

```yaml
# Simple volumeMounts generation using the helper
spec:
  template:
    spec:
      containers:
        - name: main
          image: myapp:latest
          volumeMounts: ${configurations.toContainerVolumeMounts()}

# Before - verbose manual logic:
volumeMounts: |
  ${has(configurations.configs.files) && configurations.configs.files.size() > 0 || has(configurations.secrets.files) && configurations.secrets.files.size() > 0 ?
    (has(configurations.configs.files) && configurations.configs.files.size() > 0 ?
      configurations.configs.files.map(f, {
        "name": "file-mount-"+oc_hash(f.mountPath+"/"+f.name),
        "mountPath": f.mountPath+"/"+f.name ,
        "subPath": f.name
      }) : []) +
    (has(configurations.secrets.files) && configurations.secrets.files.size() > 0 ?
      configurations.secrets.files.map(f, {
        "name": "file-mount-"+oc_hash(f.mountPath+"/"+f.name),
        "mountPath": f.mountPath+"/"+f.name,
        "subPath": f.name
      }) : [])
  : oc_omit()}

# After - clean helper usage:
volumeMounts: ${configurations.toContainerVolumeMounts()}
```

**Combining with additional mounts:**

```yaml
# Can be combined with CEL operations
volumeMounts: |
  ${configurations.toContainerVolumeMounts() +
    [{"name": "extra-mount", "mountPath": "/extra", "subPath": "extra.txt"}]}
```

#### configurations.toVolumes()

Helper method that generates a `volumes` array for all files in the configurations. This simplifies the creation of volume definitions based on all config and secret files.

The resource names are automatically generated using `metadata.componentName + "-" + metadata.environmentName` as the prefix.

**Parameters:** None

**Returns:** List of volume entries, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Volume name (generated using hash of mountPath and filename) |
| `configMap` | map | ConfigMap volume source (only present for config files) |
| `secret` | map | Secret volume source (only present for secret files) |

**Example usage:**

```yaml
# Simple volumes generation using the helper
spec:
  template:
    spec:
      containers:
        - name: main
          image: myapp:latest
          volumeMounts: ${configurations.toContainerVolumeMounts()}
      volumes: ${configurations.toVolumes()}

# Before - verbose manual logic:
volumes: |
  ${has(configurations.configs.files) && configurations.configs.files.size() > 0 || has(configurations.secrets.files) && configurations.secrets.files.size() > 0 ?
    (has(configurations.configs.files) && configurations.configs.files.size() > 0 ?
      configurations.configs.files.map(f, {
        "name": "file-mount-"+oc_hash(f.mountPath+"/"+f.name),
        "configMap": {
          "name": oc_generate_name(metadata.name, "config", f.name).replace(".", "-")
        }
      }) : []) +
    (has(configurations.secrets.files) && configurations.secrets.files.size() > 0 ?
      configurations.secrets.files.map(f, {
        "name": "file-mount-"+oc_hash(f.mountPath+"/"+f.name),
        "secret": {
          "secretName": oc_generate_name(metadata.name, "secret", f.name).replace(".", "-")
        }
      }) : [])
  : oc_omit()}

# After - clean helper usage:
volumes: ${configurations.toVolumes()}
```

**Combining with additional volumes:**

```yaml
# Can be combined with inline volumes
volumes: |
  ${configurations.toVolumes() +
    [{"name": "extra-volume", "emptyDir": {}}]}
```

### Workload Endpoint Helpers

#### workload.toServicePorts()

Helper method that converts the `workload.endpoints` map into a list of Service port definitions. This simplifies Service generation by automatically creating ports based on the workload's endpoint configuration.

**Parameters:** None

**Returns:** List of Service port objects, each containing:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Sanitized endpoint name (lowercase, alphanumeric + hyphens) |
| `port` | int | Port number from endpoint configuration |
| `targetPort` | int | Target port (same as port) |
| `protocol` | string | Kubernetes protocol (TCP or UDP) |

**Protocol mapping:**
- HTTP, REST, gRPC, GraphQL, Websocket → TCP
- TCP → TCP
- UDP → UDP

**Example usage:**

```yaml
# Simple Service port generation from workload endpoints
- id: service
  includeWhen: ${size(workload.endpoints) > 0}
  template:
    apiVersion: v1
    kind: Service
    metadata:
      name: ${metadata.name}
      namespace: ${metadata.namespace}
    spec:
      selector: ${metadata.podSelectors}
      ports: ${workload.toServicePorts()}

# Before - verbose manual logic:
ports: |
  ${workload.endpoints.transformList(name, ep, {
    "name": name.toLowerCase().replace("_", "-"),
    "port": ep.port,
    "targetPort": ep.port,
    "protocol": ep.type == "UDP" ? "UDP" : "TCP"
  })}

# After - clean helper usage:
ports: ${workload.toServicePorts()}
```

**With multiple endpoints:**

```yaml
# Given this workload:
workload:
  endpoints:
    http:
      type: HTTP
      port: 8080
    grpc:
      type: gRPC
      port: 9090

# The helper generates:
ports:
  - name: http
    port: 8080
    targetPort: 8080
    protocol: TCP
  - name: grpc
    port: 9090
    targetPort: 9090
    protocol: TCP
```

**Dynamic port references in HTTPRoute:**

```yaml
# Reference a specific endpoint's port
backendRefs:
  - name: ${metadata.componentName}
    port: ${workload.endpoints.http.port}

# Or use the first port from the service ports list
backendRefs:
  - name: ${metadata.componentName}
    port: ${workload.toServicePorts()[0].port}
```

**Notes:**
- Returns an empty list if `workload.endpoints` is empty
- Endpoint names are sanitized for Kubernetes port naming (lowercase alphanumeric + hyphens, max 15 chars)
- Duplicate names after sanitization get unique numeric suffixes (e.g., http, http-2, http-3)
- Both `port` and `targetPort` use the same value from the endpoint configuration
- Endpoints are processed in alphabetical order for deterministic output
- Use with `includeWhen: ${size(workload.endpoints) > 0}` to conditionally create Services only when endpoints exist

## See Also

- [Context Reference](./context.md) - Main context documentation



File: docs/templating/context.md
---
# Template Context Variables

This guide documents the context variables available in OpenChoreo templates. Different template locations have access to different context types.

## Overview

OpenChoreo uses two context types depending on where the template is evaluated:

| Context Type | Used In | Key Variables |
|--------------|---------|---------------|
| **ComponentContext** | ComponentType `validations` and `resources` | `metadata`, `parameters`, `environmentConfigs`, `dataplane`, `gateway`, `environment`, `workload`, `configurations`, `dependencies` |
| **TraitContext** | Trait `validations`, `creates`, and `patches` | `metadata`, `parameters`, `environmentConfigs`, `dataplane`, `gateway`, `environment`, `trait`, `workload`, `configurations`, `dependencies` |

## ComponentContext

ComponentContext is used when rendering ComponentType resources. It provides access to component metadata, parameters (from Component), environment overrides (from ReleaseBinding), workload information, and configurations.

### Available in ComponentType

| Location | Context | Notes |
|----------|---------|-------|
| `validations[].rule` | ComponentContext | Evaluated before resource rendering |
| `resources[].template` | ComponentContext | Full context |
| `resources[].includeWhen` | ComponentContext | Evaluated before forEach |
| `resources[].forEach` | ComponentContext | Expression to iterate over |
| Inside forEach iteration | ComponentContext + loop variable | Loop variable added to context |

### metadata

Platform-computed metadata for resource generation.

```yaml
# Access pattern: ${metadata.<field>}

metadata:
  # Component identity
  componentName: "my-service"           # ${metadata.componentName}
  componentUID: "a1b2c3d4-..."          # ${metadata.componentUID}

  # Project identity
  projectName: "my-project"             # ${metadata.projectName}
  projectUID: "b2c3d4e5-..."            # ${metadata.projectUID}

  # Environment identity
  environmentName: "production"         # ${metadata.environmentName}
  environmentUID: "d4e5f6g7-..."        # ${metadata.environmentUID}

  # DataPlane identity
  dataPlaneName: "my-dataplane"         # ${metadata.dataPlaneName}
  dataPlaneUID: "c3d4e5f6-..."          # ${metadata.dataPlaneUID}

  # Generated resource naming (use these in all resource templates)
  name: "my-service-dev-a1b2c3d4"       # ${metadata.name} - use as prefix for all resource names to avoid conflicts between components
  namespace: "dp-acme-corp-dev-x1y2z3"  # ${metadata.namespace} - use for all namespaced resources to ensure components in a project share the same namespace per environment

  # Common labels for all resources
  labels:                               # ${metadata.labels}
    openchoreo.dev/component: "my-service"
    openchoreo.dev/project: "my-project"
    # ... other platform labels

  # Common annotations for all resources
  annotations: {}                       # ${metadata.annotations}

  # Pod selectors - use for selector.matchLabels, pod template labels, and service selectors
  podSelectors:                         # ${metadata.podSelectors}
    openchoreo.dev/component-uid: "abc123"
    openchoreo.dev/environment-uid: "dev"
    openchoreo.dev/project-uid: "xyz789"
```

**Example usage:**

```yaml
# In ComponentType resource template
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${metadata.name}
  namespace: ${metadata.namespace}
  labels: ${metadata.labels}
spec:
  selector:
    matchLabels: ${metadata.podSelectors}
  template:
    metadata:
      labels: ${oc_merge(metadata.labels, metadata.podSelectors)}
```

### parameters

Component parameters from `Component.Spec.Parameters`, pruned to the ComponentType's `schema.parameters` section with defaults applied. Use for static configuration that doesn't change across environments.

```yaml
# Access pattern: ${parameters.<field>}

# Given this schema in ComponentType:
schema:
  parameters:
    replicas: "integer | default=1"
    port: "integer | default=8080"

# And this Component:
spec:
  parameters:
    replicas: 3

# The parameters context would be:
parameters:
  replicas: 3                    # ${parameters.replicas} (from Component)
  port: 8080                     # ${parameters.port} (default from schema)
```

**Example usage:**

```yaml
spec:
  replicas: ${parameters.replicas}
  template:
    spec:
      containers:
        - name: app
          ports:
            - containerPort: ${parameters.port}
```

### environmentConfigs

Environment-specific overrides from `ReleaseBinding.Spec.ComponentTypeEnvironmentConfigs`, pruned to the ComponentType's `schema.environmentConfigs` section with defaults applied. Use for values that vary per environment (resources, replicas, etc.).

```yaml
# Access pattern: ${environmentConfigs.<field>}

# Given this schema in ComponentType:
schema:
  environmentConfigs:
    resources:
      $default: {}
      requests:
        $default: {}
        cpu: "string | default=100m"
        memory: "string | default=128Mi"
      limits:
        $default: {}
        cpu: "string | default=500m"
        memory: "string | default=512Mi"

# And this ReleaseBinding:
spec:
  componentTypeEnvironmentConfigs:
    resources:
      requests:
        cpu: "200m"
        memory: "256Mi"

# The environmentConfigs context would be:
environmentConfigs:
  resources:
    requests:
      cpu: "200m"                # ${environmentConfigs.resources.requests.cpu} (from ReleaseBinding)
      memory: "256Mi"            # ${environmentConfigs.resources.requests.memory} (from ReleaseBinding)
    limits:
      cpu: "500m"                # ${environmentConfigs.resources.limits.cpu} (default)
      memory: "512Mi"            # ${environmentConfigs.resources.limits.memory} (default)
```

**Example usage:**

```yaml
spec:
  template:
    spec:
      containers:
        - name: app
          resources:
            requests:
              cpu: ${environmentConfigs.resources.requests.cpu}
              memory: ${environmentConfigs.resources.requests.memory}
            limits:
              cpu: ${environmentConfigs.resources.limits.cpu}
              memory: ${environmentConfigs.resources.limits.memory}
```

**Key difference from parameters:**
- `parameters`: Static values from Component - same across all environments
- `environmentConfigs`: Environment-specific values from ReleaseBinding - different per environment

### dataplane

DataPlane configuration for the target environment.

```yaml
# Access pattern: ${dataplane.<field>}

dataplane:
  secretStore: "my-secret-store"              # ${dataplane.secretStore}
  gateway:                                    # ${dataplane.gateway}
    ingress:                                  # ${dataplane.gateway.ingress}
      external:                               # ${dataplane.gateway.ingress.external}
        name: "gateway-default"               # ${dataplane.gateway.ingress.external.name}
        namespace: "openchoreo-data-plane"     # ${dataplane.gateway.ingress.external.namespace}
        http:                                 # ${dataplane.gateway.ingress.external.http}
          listenerName: "http"                # ${dataplane.gateway.ingress.external.http.listenerName}
          port: 8080                          # ${dataplane.gateway.ingress.external.http.port}
          host: "app.example.com"             # ${dataplane.gateway.ingress.external.http.host}
        https:                                # ${dataplane.gateway.ingress.external.https}
          listenerName: "https"
          port: 8443
          host: "app.example.com"
  observabilityPlaneRef:                      # ${dataplane.observabilityPlaneRef}
    kind: "ObservabilityPlane"                # ${dataplane.observabilityPlaneRef.kind} - "ObservabilityPlane" or "ClusterObservabilityPlane"
    name: "my-obs-plane"                      # ${dataplane.observabilityPlaneRef.name}
```

**Optional fields:** `secretStore`, `gateway`, and `observabilityPlaneRef` are optional. If not configured on the DataPlane, the field will be absent from the context. Use `has()` to guard conditional logic:

```yaml
# Guard with has() for conditional inclusion
includeWhen: ${has(dataplane.secretStore)}

# Or use ternary for conditional values
secretStoreRef: ${has(dataplane.secretStore) ? {"name": dataplane.secretStore} : oc_omit()}
```

**Example usage:**

```yaml
# Creating an ExternalSecret that references the dataplane's secret store
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: ${metadata.name}
spec:
  secretStoreRef:
    name: ${dataplane.secretStore}
    kind: ClusterSecretStore
```

### gateway

Top-level gateway configuration resolved for the component's environment. If the environment has its own gateway configuration, it takes precedence over the dataplane gateway.

```yaml
# Access pattern: ${gateway.<field>}

gateway:
  ingress:
    external:
      name: "gateway-default"                 # ${gateway.ingress.external.name}
      namespace: "openchoreo-data-plane"       # ${gateway.ingress.external.namespace}
      http:
        listenerName: "http"                   # ${gateway.ingress.external.http.listenerName}
        port: 8080                             # ${gateway.ingress.external.http.port}
        host: "app.example.com"                # ${gateway.ingress.external.http.host}
      https:
        listenerName: "https"                  # ${gateway.ingress.external.https.listenerName}
        port: 8443                             # ${gateway.ingress.external.https.port}
        host: "app.example.com"               # ${gateway.ingress.external.https.host}
    internal:
      name: "gateway-internal"                 # ${gateway.ingress.internal.name}
      namespace: "openchoreo-data-plane"       # ${gateway.ingress.internal.namespace}
```

**Optional:** The `gateway` field is optional. Use `has()` to guard conditional logic.

### environment

Environment-specific configuration for the target environment.

```yaml
# Access pattern: ${environment.<field>}

environment:
  gateway:                                     # ${environment.gateway} - environment-specific gateway overrides
    ingress:
      external:
        name: "env-gateway"
  defaultNotificationChannel: "my-channel"     # ${environment.defaultNotificationChannel}
```

**Optional:** The `environment` fields are optional. If the environment does not have specific gateway configuration, the dataplane gateway is used as a fallback via the top-level `gateway` variable.

### workload

Workload specification containing container and endpoint information from the build process.

```yaml
# Access pattern: ${workload.container.<field>}

workload:
  container:                              # ${workload.container}
    image: "myregistry/myapp:v1.0"        # ${workload.container.image}
    command: ["./start.sh"]               # ${workload.container.command}
    args: ["--port", "8080"]              # ${workload.container.args}
  endpoints:
    http:                               # ${workload.endpoints.http}
      type: "HTTP"                      # ${workload.endpoints.http.type}
      port: 8080                        # ${workload.endpoints.http.port}
      basePath: "/api"                  # ${workload.endpoints.http.basePath} (optional, default "/")
      visibility: ["project", "external"] # ${workload.endpoints.http.visibility}
      schema:                           # ${workload.endpoints.http.schema} (optional)
        type: "openapi"
        content: "..."
    grpc:
      type: "gRPC"
      port: 9090
      visibility: ["project"]           # project visibility only - no gateway routes created
```

**Endpoint types:** HTTP, gRPC, GraphQL, Websocket, TCP, UDP

**Endpoint visibility:** Endpoints always include `"project"` visibility. Additional scopes — `"external"` and `"internal"` — determine which gateway HTTPRoutes are created:

| Visibility scope | Effect |
|-----------------|--------|
| `project` | Always present; endpoint is reachable within the project namespace (no gateway route) |
| `external` | Creates an HTTPRoute on the external ingress gateway |
| `internal` | Creates an HTTPRoute on the internal ingress gateway |

**Example usage:**

```yaml
spec:
  template:
    spec:
      containers:
        - name: app
          image: ${workload.container.image}
          command: ${workload.container.command}
          args: ${workload.container.args}
```

**Iterating over endpoints by visibility (recommended pattern for HTTPRoute generation):**

```yaml
# Create HTTPRoutes only for endpoints with external visibility
- id: httproute-external
  forEach: '${workload.endpoints.transformMap(name, ep, "external" in ep.visibility && ep.type in ["HTTP", "GraphQL", "Websocket"], ep)}'
  var: endpoint
  template:
    apiVersion: gateway.networking.k8s.io/v1
    kind: HTTPRoute
    metadata:
      name: ${oc_generate_name(metadata.componentName, endpoint.key)}
      namespace: ${metadata.namespace}
      labels: '${oc_merge(metadata.labels, {"openchoreo.dev/endpoint-name": endpoint.key, "openchoreo.dev/endpoint-visibility": "external"})}'
    spec:
      parentRefs:
        - name: ${gateway.ingress.external.name}
          namespace: ${gateway.ingress.external.namespace}
      hostnames: |
        ${[gateway.ingress.external.?http, gateway.ingress.external.?https]
          .filter(g, g.hasValue()).map(g, g.value().host).distinct()
          .map(h, metadata.environmentName + "-" + metadata.componentNamespace + "." + h)}
      rules:
      - matches:
        - path:
            type: PathPrefix
            value: /${metadata.componentName}-${endpoint.key}
        filters:
          - type: URLRewrite
            urlRewrite:
              path:
                type: ReplacePrefixMatch
                replacePrefixMatch: '${endpoint.value.?basePath.orValue("/")}'
        backendRefs:
        - name: ${metadata.componentName}
          port: ${endpoint.value.port}

# Create HTTPRoutes only for endpoints with internal visibility
- id: httproute-internal
  forEach: '${workload.endpoints.transformMap(name, ep, "internal" in ep.visibility && ep.type in ["HTTP", "GraphQL", "Websocket"], ep)}'
  var: endpoint
  template:
    apiVersion: gateway.networking.k8s.io/v1
    kind: HTTPRoute
    metadata:
      name: '${oc_generate_name(metadata.componentName, endpoint.key, "internal")}'
      namespace: ${metadata.namespace}
      labels: '${oc_merge(metadata.labels, {"openchoreo.dev/endpoint-name": endpoint.key, "openchoreo.dev/endpoint-visibility": "internal"})}'
    spec:
      parentRefs:
        - name: ${gateway.ingress.internal.name}
          namespace: ${gateway.ingress.internal.namespace}
      hostnames: |
        ${[gateway.ingress.internal.?http, gateway.ingress.internal.?https]
          .filter(g, g.hasValue()).map(g, g.value().host).distinct()
          .map(h, metadata.environmentName + "-" + metadata.componentNamespace + "." + h)}
      rules:
      - matches:
        - path:
            type: PathPrefix
            value: /${metadata.componentName}-${endpoint.key}
        filters:
          - type: URLRewrite
            urlRewrite:
              path:
                type: ReplacePrefixMatch
                replacePrefixMatch: '${endpoint.value.?basePath.orValue("/")}'
        backendRefs:
        - name: ${metadata.componentName}
          port: ${endpoint.value.port}
```

**Iterating over all endpoints (generic pattern):**

```yaml
# Using transformList to convert endpoints map to list of ports
ports: |
  ${workload.endpoints.transformList(name, ep, {
    "name": name,
    "port": ep.port,
    "protocol": ep.type == "UDP" ? "UDP" : "TCP"
  })}
```

**Workload Endpoint Helper Method:**

The `workload` object provides a helper method to simplify Service port generation:

| Helper Method | Description |
|---------------|-------------|
| `workload.toServicePorts()` | Converts endpoints map to Service ports list with proper protocol mapping and name sanitization |

For detailed documentation and examples, see [Configuration Helpers - Workload Endpoint Helpers](./configuration_helpers.md#workload-endpoint-helpers).

**Quick Example:**

```yaml
# Using helper method for cleaner Service generation
- id: service
  includeWhen: ${size(workload.endpoints) > 0}
  template:
    spec:
      ports: ${workload.toServicePorts()}
```

### configurations

Configuration items (environment variables and files) extracted from workload.

```yaml
# Access pattern: ${configurations.<field>}

configurations:                           # ${configurations}
  configs:                                # ${configurations.configs}
    envs:                                 # ${configurations.configs.envs}
      - name: "DATABASE_URL"
        value: "postgres://..."
      - name: "LOG_LEVEL"
        value: "info"
    files:                                # ${configurations.configs.files}
      - name: "config.yaml"
        mountPath: "/etc/app/config.yaml"
        value: "key: value\n..."
  secrets:                                # ${configurations.secrets}
    envs:                                 # ${configurations.secrets.envs}
      - name: "API_KEY"
        remoteRef:
          key: "my-secret"
          property: "api-key"
    files:                                # ${configurations.secrets.files}
      - name: "credentials.json"
        mountPath: "/etc/app/credentials.json"
        remoteRef:
          key: "my-secret"
          property: "credentials"
```

**Structure details:**

| Field | Type | Description |
|-------|------|-------------|
| `configurations.configs.envs` | `[]EnvConfiguration` | Plain config environment variables |
| `configurations.configs.files` | `[]FileConfiguration` | Plain config files |
| `configurations.secrets.envs` | `[]EnvConfiguration` | Secret environment variables |
| `configurations.secrets.files` | `[]FileConfiguration` | Secret files |

**EnvConfiguration structure:**

```yaml
- name: "VAR_NAME"              # Environment variable name
  value: "plain-value"          # Plain text value (for configs)
  remoteRef:                    # Remote reference (for secrets)
    key: "secret-name"
    property: "secret-key"
    version: "v1"               # Optional
```

**FileConfiguration structure:**

```yaml
- name: "filename.txt"          # File name
  mountPath: "/path/to/file"    # Where to mount the file
  value: "file-contents"        # Plain text content (for configs)
  remoteRef:                    # Remote reference (for secrets)
    key: "secret-name"
    property: "secret-key"
```

**Example usage:**

```yaml
# Inject environment variables from configurations
env: |
  ${configurations.configs.envs.map(e, {
    "name": e.name,
    "value": e.value
  })}

# Create ConfigMap from config files
data: |
  ${configurations.configs.files.transformMapEntry(i, f, {f.name: f.value})}

# Check for config envs before creating configMapRef
envFrom: |
  ${has(configurations.configs.envs) &&
   configurations.configs.envs.size() > 0 ?
    [{"configMapRef": {"name": metadata.name + "-config"}}] : []}
```

### dependencies

Dependency information for connections declared by the component. Contains both per-connection metadata and a merged flat list of all resolved environment variables.

```yaml
# Access pattern: ${dependencies.<field>}

dependencies:                                 # ${dependencies}
  items:                                      # ${dependencies.items}
    - namespace: "ns1"                        # ${dependencies.items[0].namespace} - target component's namespace
      project: "proj1"                        # ${dependencies.items[0].project} - target project name
      component: "svc-a"                      # ${dependencies.items[0].component} - target component name
      endpoint: "http"                        # ${dependencies.items[0].endpoint} - target endpoint name
      visibility: "project"                   # ${dependencies.items[0].visibility} - resolved visibility level
      envVars:                                # ${dependencies.items[0].envVars} - per-connection env vars
        - name: "SVC_A_URL"
          value: "http://svc-a:8080"
    - namespace: "ns1"
      project: "proj1"
      component: "svc-b"
      endpoint: "grpc"
      visibility: "namespace"
      envVars:
        - name: "SVC_B_URL"
          value: "grpc://svc-b:9090"
        - name: "SVC_B_HOST"
          value: "svc-b"
  envVars:                                    # ${dependencies.envVars} - merged flat list of ALL env vars from all items
    - name: "SVC_A_URL"
      value: "http://svc-a:8080"
    - name: "SVC_B_URL"
      value: "grpc://svc-b:9090"
    - name: "SVC_B_HOST"
      value: "svc-b"
```

**Structure details:**

| Field | Type | Description |
|-------|------|-------------|
| `dependencies.items` | `[]ConnectionItem` | List of resolved connections with metadata and per-item env vars |
| `dependencies.envVars` | `[]ConnectionEnvVar` | Merged flat list of all env vars from all connection items |

**ConnectionItem structure:**

| Field | Type | Description |
|-------|------|-------------|
| `namespace` | `string` | Target component's control plane namespace |
| `project` | `string` | Target project name |
| `component` | `string` | Target component name |
| `endpoint` | `string` | Target endpoint name |
| `visibility` | `string` | Resolved visibility level (e.g., `project`, `namespace`, `internal`, `external`) |
| `envVars` | `[]ConnectionEnvVar` | Environment variables resolved for this connection |

**ConnectionEnvVar structure:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Environment variable name |
| `value` | `string` | Resolved environment variable value |

**Example usage:**

```yaml
# Inject all dependency env vars into a container
env: |
  ${dependencies.envVars.map(e, {
    "name": e.name,
    "value": e.value
  })}

# Iterate over individual connection items
forEach: ${dependencies.items}
var: dep
template:
  # Use dep.component, dep.endpoint, dep.envVars, etc.
```

**Note:** If no dependencies are configured, both `items` and `envVars` will be empty lists (never null), so CEL expressions like `dependencies.envVars.size()` are always safe to call.

### Dependency Helper Methods

The `dependencies` object provides a helper method to simplify injecting connection environment variables into containers.

| Helper Method | Description |
|---------------|-------------|
| `dependencies.toContainerEnvs()` | Returns the merged flat list of all dependency env vars (equivalent to `dependencies.envVars`) |

**Example usage:**

```yaml
# Using the helper method for cleaner container env injection
spec:
  template:
    spec:
      containers:
        - name: app
          env: ${dependencies.toContainerEnvs()}
```

### Configuration Helper Methods

The `configurations` object provides several helper methods to simplify working with container configurations, environment variables, and file mounts. These helpers reduce boilerplate and make templates more readable.

**Available Helper Methods:**

| Helper Method | Description |
|---------------|-------------|
| `configurations.toContainerEnvFrom()` | Generates `envFrom` array with configMapRef and secretRef |
| `configurations.toConfigEnvsByContainer()` | Returns list of config environment variables |
| `configurations.toSecretEnvsByContainer()` | Returns list of secret environment variables |
| `configurations.toConfigFileList()` | Flattens all config files into a single list |
| `configurations.toSecretFileList()` | Flattens all secret files into a single list |
| `configurations.toContainerVolumeMounts()` | Generates volumeMounts array for the container's files |
| `configurations.toVolumes()` | Generates volumes array for all files |

For detailed documentation, examples, and usage patterns for each helper method, see [Configuration Helpers](./configuration_helpers.md).

**Quick Example:**

```yaml
# Using helper methods for cleaner templates
spec:
  template:
    spec:
      containers:
        - name: main
          image: myapp:latest
          envFrom: ${configurations.toContainerEnvFrom()}
          volumeMounts: ${configurations.toContainerVolumeMounts()}
      volumes: ${configurations.toVolumes()}
```

## TraitContext

TraitContext is used when rendering Trait creates and patches. It provides access to metadata, trait-specific information, parameters (from trait instance), and environment overrides (from ReleaseBinding).

### Available in Traits

| Location | Context | Notes |
|----------|---------|-------|
| `validations[].rule` | TraitContext | Evaluated before creates/patches |
| `creates[].template` | TraitContext | Full trait context |
| `patches[].operations[].path` | TraitContext | Path can contain expressions |
| `patches[].operations[].value` | TraitContext | Value can contain expressions |
| `patches[].forEach` | TraitContext | Expression to iterate over |
| Inside forEach iteration | TraitContext + loop variable | Loop variable added |
| `patches[].target.where` | TraitContext + `resource` | Special `resource` variable added |

### metadata

Same structure as ComponentContext metadata. See [metadata](#metadata) above.

### trait

Trait-specific metadata identifying the trait and its instance.

```yaml
# Access pattern: ${trait.<field>}

trait:
  name: "storage"                # ${trait.name} - Trait CRD name
  instanceName: "my-storage"     # ${trait.instanceName} - Instance name in Component
```

**Example usage:**

```yaml
# In Trait creates template
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${oc_generate_name(metadata.name, trait.instanceName)}
  labels:
    trait: ${trait.name}
    instance: ${trait.instanceName}
```

### dataplane

DataPlane configuration for the target environment. Same structure as ComponentContext. The fields `secretStore`, `publicVirtualHost`, and `observabilityPlaneRef` are optional; use `has()` to guard conditional logic.

```yaml
# Access pattern: ${dataplane.<field>}

dataplane:
  secretStore: "my-secret-store"              # ${dataplane.secretStore}
  publicVirtualHost: "app.example.com"        # ${dataplane.publicVirtualHost}
  observabilityPlaneRef:                      # ${dataplane.observabilityPlaneRef}
    kind: "ObservabilityPlane"                # ${dataplane.observabilityPlaneRef.kind} - "ObservabilityPlane" or "ClusterObservabilityPlane"
    name: "my-obs-plane"                      # ${dataplane.observabilityPlaneRef.name}
```

### parameters

Trait instance parameters from `Component.Spec.Traits[].Parameters`, pruned to the Trait's `schema.parameters` section with defaults applied. Use for static configuration that doesn't change across environments.

```yaml
# Given this schema in Trait:
schema:
  parameters:
    volumeName: "string"
    mountPath: "string"
    containerName: "string | default=app"

# And this trait instance in Component:
traits:
  - name: persistent-volume
    instanceName: data-storage
    parameters:
      volumeName: "app-data"
      mountPath: "/var/data"

# The parameters context would be:
parameters:
  volumeName: "app-data"         # ${parameters.volumeName} (from trait instance)
  mountPath: "/var/data"         # ${parameters.mountPath} (from trait instance)
  containerName: "app"           # ${parameters.containerName} (default)
```

### environmentConfigs

Environment-specific overrides from `ReleaseBinding.Spec.TraitEnvironmentConfigs[instanceName]`, pruned to the Trait's `schema.environmentConfigs` section with defaults applied. Use for values that vary per environment.

```yaml
# Given this schema in Trait:
schema:
  environmentConfigs:
    size: "string | default=10Gi"
    storageClass: "string | default=standard"

# And this ReleaseBinding:
spec:
  traitEnvironmentConfigs:
    data-storage:              # keyed by instanceName
      size: "50Gi"
      storageClass: "fast-ssd"

# The environmentConfigs context would be:
environmentConfigs:
  size: "50Gi"                   # ${environmentConfigs.size} (from ReleaseBinding)
  storageClass: "fast-ssd"       # ${environmentConfigs.storageClass} (from ReleaseBinding)
```

**Example usage:**

```yaml
# In Trait creates template
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${metadata.name}-${trait.instanceName}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: ${environmentConfigs.size}
  storageClassName: ${environmentConfigs.storageClass}
```

### workload

Workload specification containing container and endpoint information. Same structure as ComponentContext workload. See [workload](#workload) section above for full details.

```yaml
# Access pattern: ${workload.<field>}

workload:
  container:
    image: "myregistry/myapp:v1.0"
    command: ["./start.sh"]
    args: ["--port", "8080"]
  endpoints:
    http:
      type: "HTTP"
      port: 8080
```

### configurations

Configuration items (environment variables and files) extracted from workload. Same structure as ComponentContext configurations. See [configurations](#configurations) section above for full details and helper methods.

```yaml
# Access pattern: ${configurations.<field>}

configurations:                           # ${configurations}
  configs:                                # ${configurations.configs}
    envs: [...]                           # ${configurations.configs.envs}
    files: [...]                          # ${configurations.configs.files}
  secrets:                                # ${configurations.secrets}
    envs: [...]                           # ${configurations.secrets.envs}
    files: [...]                          # ${configurations.secrets.files}
```

**Available helper methods** (same as ComponentContext):
- `configurations.toContainerEnvFrom()`
- `configurations.toConfigEnvsByContainer()`
- `configurations.toSecretEnvsByContainer()`
- `configurations.toConfigFileList()`
- `configurations.toSecretFileList()`
- `configurations.toContainerVolumeMounts()`
- `configurations.toVolumes()`

### dependencies

Dependency information for connections. Same structure as ComponentContext dependencies. See [dependencies](#dependencies) section above for full details and helper methods.

```yaml
# Access pattern: ${dependencies.<field>}

dependencies:                                 # ${dependencies}
  items: [...]                               # ${dependencies.items} - per-connection metadata and env vars
  envVars: [...]                             # ${dependencies.envVars} - merged flat list of all env vars
```

**Available helper methods** (same as ComponentContext):
- `dependencies.toContainerEnvs()`

## Special Variables

### Loop Variables (forEach)

When using `forEach`, the loop variable is added to the context for each iteration.

```yaml
# ComponentType resource with forEach
resources:
  - forEach: ${parameters.ports}
    var: port                    # Loop variable name (defaults to "item")
    resource:
      apiVersion: v1
      kind: Service
      metadata:
        name: ${oc_generate_name(metadata.name, port.name)}
      spec:
        ports:
          - port: ${port.port}   # Access loop variable
            name: ${port.name}

# Trait patch with forEach
patches:
  - forEach: ${parameters.volumes}
    var: vol
    target:
      kind: Deployment
    operations:
      - op: add
        path: /spec/template/spec/volumes/-
        value:
          name: ${vol.name}
          persistentVolumeClaim:
            claimName: ${vol.claimName}
```

### resource Variable (where clause)

In trait patch `where` clauses, the `resource` variable provides access to the target resource being evaluated.

```yaml
patches:
  - target:
      kind: Deployment
      # Filter to only patch deployments with specific label
      where: ${resource.metadata.labels["app.kubernetes.io/component"] == "backend"}
    operations:
      - op: add
        path: /spec/template/spec/containers/0/env/-
        value:
          name: BACKEND_MODE
          value: "true"

  - target:
      kind: Service
      # Filter based on service type
      where: ${resource.spec.type == "LoadBalancer"}
    operations:
      - op: add
        path: /metadata/annotations/service.beta.kubernetes.io~1aws-load-balancer-type
        value: "nlb"
```

**Available in `resource`:**

The entire rendered Kubernetes resource is available, including:
- `resource.apiVersion`
- `resource.kind`
- `resource.metadata` (name, namespace, labels, annotations, etc.)
- `resource.spec` (resource-specific specification)

## Context Comparison

| Variable | ComponentContext | TraitContext |
|----------|------------------|--------------|
| `metadata.*` | ✅ | ✅ |
| `parameters.*` | ✅ (from Component.Spec.Parameters) | ✅ (from Trait instance) |
| `environmentConfigs.*` | ✅ (from ReleaseBinding.ComponentTypeEnvironmentConfigs) | ✅ (from ReleaseBinding.TraitEnvironmentConfigs) |
| `dataplane.*` | ✅ | ✅ |
| `gateway.*` | ✅ | ✅ |
| `environment.*` | ✅ | ✅ |
| `workload.*` | ✅ | ✅ |
| `configurations.*` | ✅ | ✅ |
| `dependencies.*` | ✅ | ✅ |
| `trait.*` | ❌ | ✅ |
| Loop variable | ✅ (in forEach) | ✅ (in forEach) |
| `resource` | ❌ | ✅ (in where only) |



File: docs/templating/openapiv3-schema.md
---
# openAPIV3Schema

This guide explains how to define schemas for ComponentTypes, Traits, and Workflows using standard **OpenAPI V3 / JSON Schema** format (`openAPIV3Schema`). This is the schema format for all OpenChoreo resources, providing full compatibility with the OpenAPI specification and enabling richer tooling integration.

## Overview

Schemas allow you to define parameter validation rules for ComponentTypes, Traits, and Workflows. The `openAPIV3Schema` format uses standard JSON Schema syntax, giving you access to the full set of JSON Schema features.

```yaml
parameters:
  openAPIV3Schema:
    type: object
    properties:
      replicas:
        type: integer
        default: 1
        minimum: 1
        maximum: 100
      image:
        type: string
        description: "Container image to deploy"
    required:
      - image
```

## Basic Syntax

### Simple Types

```yaml
openAPIV3Schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
      minimum: 0
      maximum: 120
    price:
      type: number
      minimum: 0.01
    enabled:
      type: boolean
      default: false
```

### Required Fields

In `openAPIV3Schema` you explicitly list required fields. Fields not listed in `required` are optional:

```yaml
openAPIV3Schema:
  type: object
  properties:
    name:
      type: string                  # required (listed below)
    replicas:
      type: integer
      default: 1                    # optional (has default, not in required)
    description:
      type: string                  # optional (not in required)
  required:
    - name
```

### Enums

```yaml
openAPIV3Schema:
  type: object
  properties:
    environment:
      type: string
      enum:
        - dev
        - staging
        - prod
      default: dev
    severity:
      type: string
      enum: [info, warning, critical]
      default: warning
```

### Arrays

```yaml
openAPIV3Schema:
  type: object
  properties:
    tags:
      type: array
      items:
        type: string
      default:
        - default
      minItems: 1
      maxItems: 10
    containers:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
          image:
            type: string
          port:
            type: integer
            default: 8080
        required:
          - name
          - image
```

### Maps (additionalProperties)

```yaml
openAPIV3Schema:
  type: object
  properties:
    labels:
      type: object
      additionalProperties:
        type: string
      default: {}
    ports:
      type: object
      additionalProperties:
        type: integer
```

### Nested Objects

```yaml
openAPIV3Schema:
  type: object
  properties:
    database:
      type: object
      properties:
        host:
          type: string
        port:
          type: integer
          default: 5432
        credentials:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
      required:
        - host
```

## Reusable Types with $defs and $ref

Use `$defs` to define reusable type definitions and `$ref` to reference them. This avoids duplication and keeps schemas maintainable.

```yaml
openAPIV3Schema:
  type: object
  $defs:
    ResourceQuantity:
      type: object
      default: {}
      properties:
        cpu:
          type: string
          default: "100m"
        memory:
          type: string
          default: "256Mi"
    ResourceRequirements:
      type: object
      default: {}
      properties:
        requests:
          $ref: "#/$defs/ResourceQuantity"
        limits:
          $ref: "#/$defs/ResourceQuantity"
  properties:
    resources:
      $ref: "#/$defs/ResourceRequirements"
```

### $ref with Sibling Keys

OpenChoreo supports JSON Schema 2020-12 semantics where `$ref` can have sibling keys. Sibling keys override the referenced definition on conflict:

```yaml
properties:
  resources:
    $ref: "#/$defs/ResourceRequirements"
    default: {}                              # overrides the definition's default
    x-openchoreo-resources-portal:           # vendor extension as sibling
      ui:field: ResourcePicker
```

### $ref Resolution Rules

- Only **local** `$ref` paths are supported: `#/$defs/Name`
- The older `definitions` keyword (JSON Schema Draft 4/7) is **not** supported — use `$defs` (JSON Schema 2020-12)
- Remote/URL refs (e.g., `http://...`) are rejected
- **Circular references** are detected and rejected with descriptive errors
- References are resolved recursively (chained refs like `A -> B -> C` work)
- Maximum resolution depth is 64 levels
- After resolution, `$defs` is removed from the output

## Vendor Extensions (x-*)

You can add custom `x-*` keys to any schema node. These are preserved in API responses (e.g., `/componenttypes/{name}/schema`) for consumption by frontends and portals:

```yaml
openAPIV3Schema:
  type: object
  $defs:
    ResourceRequirements:
      type: object
      properties:
        cpu:
          type: string
          default: "250m"
        memory:
          type: string
          default: "256Mi"
  properties:
    repository:
      type: object
      properties:
        url:
          type: string
          description: "Git repository URL"
          x-openchoreo-backstage-portal:
            ui:field: RepoUrlPicker
            ui:options:
              allowedHosts:
                - github.com
        branch:
          type: string
          default: main
          x-openchoreo-backstage-portal:
            ui:widget: text
    resources:
      $ref: "#/$defs/ResourceRequirements"
      x-openchoreo-resources-portal:
        ui:field: ResourcePicker
```

**Important:** Vendor extensions are:
- **Preserved** in API schema responses (`SectionToRawJSONSchema`)
- **Stripped** from Kubernetes structural schemas (K8s rejects `x-*` keys)
- **Not used** in validation — they are metadata only

## Defaults

### How Defaults Work

Defaults follow standard Kubernetes defaulting behavior:

1. Missing fields with `default` values are populated automatically
2. Existing fields are never overwritten
3. Nested object defaults require `default: {}` at each level for the defaulting engine to traverse into them

### Primitive, Array, and Map Defaults

```yaml
properties:
  # Required — no default, must provide value
  name:
    type: string

  # Optional — has default
  replicas:
    type: integer
    default: 1

  # Optional array
  tags:
    type: array
    items:
      type: string
    default: []

  # Optional map
  labels:
    type: object
    additionalProperties:
      type: string
    default: {}
required:
  - name
```

### Nested Object Defaults

For Kubernetes defaulting to create nested objects, **each level needs its own `default: {}`**. Without it, the defaulting engine will not traverse into the object and nested defaults will not be applied.

```yaml
$defs:
  ResourceQuantity:
    type: object
    default: {}          # Required: tells K8s to create this object
    properties:
      cpu:
        type: string
        default: "100m"
      memory:
        type: string
        default: "256Mi"
  ResourceRequirements:
    type: object
    default: {}          # Required: tells K8s to create this object
    properties:
      requests:
        $ref: "#/$defs/ResourceQuantity"
      limits:
        $ref: "#/$defs/ResourceQuantity"
properties:
  resources:
    $ref: "#/$defs/ResourceRequirements"
```

With the above, providing `{}` for parameters will result in:
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "100m"
    memory: "256Mi"
```

Without `default: {}` on the intermediate objects, nested defaults will **not** be applied.

### Overriding Defaults via $ref Siblings

When a field references a type via `$ref` and also specifies a `default` as a sibling key, the sibling default takes precedence over the definition's default:

```yaml
$defs:
  Resources:
    type: object
    default:
      cpu: "100m"
      memory: "128Mi"
    properties:
      cpu:
        type: string
      memory:
        type: string
    required: [cpu, memory]
properties:
  # Sibling default overrides the definition's default
  resources:
    $ref: "#/$defs/Resources"
    default:
      cpu: "500m"
      memory: "256Mi"
```

This allows types to provide sensible defaults that can be customized at each usage site.

### Default Precedence Summary

When a user provides an object, field-level defaults apply to any missing fields within it. When a user does not provide an object at all, the object-level `default` is used, then field-level defaults fill in any remaining gaps. Providing an object overrides the entire object default (no merging) — this follows standard JSON Schema semantics.

```yaml
# Schema:
database:
  type: object
  default:
    host: "localhost"
  properties:
    host:
      type: string
    port:
      type: integer
      default: 5432
  required:
    - host

# When user provides nothing → database = {host: "localhost", port: 5432}
# When user provides {host: "production-db"} → database = {host: "production-db", port: 5432}
```

## String Constraints

```yaml
username:
  type: string
  minLength: 3
  maxLength: 20
  pattern: "^[a-z][a-z0-9_]*$"
email:
  type: string
  format: email
version:
  type: string
  pattern: "^v\\d+\\.\\d+\\.\\d+$"
  default: "v1.0.0"
```

## Numeric Constraints

```yaml
replicas:
  type: integer
  minimum: 1
  maximum: 100
  default: 1
threshold:
  type: number
  minimum: 0
  maximum: 1
  exclusiveMinimum: true
  default: 0.75
statusCode:
  type: integer
  enum: [200, 201, 204, 400, 404, 500]
```

## Array Constraints

```yaml
tags:
  type: array
  items:
    type: string
  minItems: 1
  maxItems: 10
```

## Map Constraints

```yaml
metadata:
  type: object
  additionalProperties:
    type: string
  minProperties: 1
  maxProperties: 10
```

## Descriptions and Documentation

```yaml
openAPIV3Schema:
  type: object
  properties:
    replicas:
      type: integer
      default: 1
      description: "Number of pod replicas to run"
    image:
      type: string
      description: "Container image to deploy"
    environment:
      type: string
      enum: [dev, staging, prod]
      default: dev
      description: "Target deployment environment"
```

Descriptions are preserved in API responses and can be used by UI generators.

## Complete Examples

### ComponentType with openAPIV3Schema

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: ComponentType
metadata:
  name: service
spec:
  workloadType: deployment

  environmentConfigs:
    openAPIV3Schema:
      type: object
      $defs:
        ResourceQuantity:
          type: object
          default: {}
          properties:
            cpu:
              type: string
              default: "100m"
            memory:
              type: string
              default: "256Mi"
        ResourceRequirements:
          type: object
          default: {}
          properties:
            requests:
              $ref: "#/$defs/ResourceQuantity"
            limits:
              $ref: "#/$defs/ResourceQuantity"
      properties:
        replicas:
          type: integer
          default: 1
        resources:
          $ref: "#/$defs/ResourceRequirements"
        imagePullPolicy:
          type: string
          default: IfNotPresent

  resources:
    - id: deployment
      template:
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: ${metadata.name}
        spec:
          replicas: ${environmentConfigs.replicas}
          # ... rest of template
```

### Trait with openAPIV3Schema

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Trait
metadata:
  name: observability-alert-rule
spec:
  parameters:
    openAPIV3Schema:
      type: object
      properties:
        description:
          type: string
          description: "Human-readable description of the alert rule"
        severity:
          type: string
          enum: [info, warning, critical]
          default: warning
        source:
          type: object
          properties:
            type:
              type: string
              enum: [log, metric]
            query:
              type: string
              default: ""
          required:
            - type
      required:
        - description
        - source

  environmentConfigs:
    openAPIV3Schema:
      type: object
      properties:
        enabled:
          type: boolean
          default: true
        actions:
          type: object
          properties:
            notifications:
              type: object
              properties:
                channels:
                  type: array
                  items:
                    type: string
                  default: []
```

### Workflow with openAPIV3Schema

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: Workflow
metadata:
  name: docker
spec:
  parameters:
    openAPIV3Schema:
      type: object
      required:
        - repository
      properties:
        repository:
          type: object
          required:
            - url
          properties:
            url:
              type: string
              description: "Git repository URL"
            secretRef:
              type: string
              default: ""
            revision:
              type: object
              default: {}
              properties:
                branch:
                  type: string
                  default: main
                commit:
                  type: string
                  default: ""
            appPath:
              type: string
              default: "."
        docker:
          type: object
          default: {}
          properties:
            context:
              type: string
              default: "."
            filePath:
              type: string
              default: "./Dockerfile"
  # ... rest of workflow spec
```



File: docs/templating/patching.md
---
# Patching

This guide explains how to use the patching system in OpenChoreo Traits to modify resources generated by ComponentTypes. The patching engine extends standard JSON Patch (RFC 6902) with powerful features like array filtering and automatic parent creation.

## Overview

Traits can modify existing resources using patches, which are JSON Patch operations enhanced with:
- Array filtering using JSONPath-like syntax
- Automatic parent map creation
- CEL-based resource targeting
- forEach iteration support

## Basic Patch Structure

Patches are defined in the Trait's `spec.patches` section:

```yaml
apiVersion: v1alpha1
kind: Trait
metadata:
  name: monitoring-sidecar
spec:
  patches:
    - target:
        kind: Deployment
        group: apps
        version: v1
      targetPlane: dataplane
      operations:
        - op: add
          path: /spec/template/spec/containers/-
          value:
            name: prometheus-exporter
            image: prom/node-exporter:latest
            ports:
            - containerPort: 9100
```

## CEL Expression Support

CEL expressions (enclosed in `${...}`) can be used in the following patch fields:

- **`forEach`** - Iterate over lists from parameters or metadata
  ```yaml
  forEach: ${parameters.environments}
  ```

- **`where`** - Conditionally apply patches based on resource properties
  ```yaml
  where: ${resource.spec.replicas > 1}
  ```

- **`path`** - Dynamic path segments and array filter conditions
  ```yaml
  path: /data/${env.name}
  path: /spec/containers[?(@.name=='${metadata.name}')]/env/-
  ```

- **`value`** - The value to set. Can be:

  Literal value:
  ```yaml
  value: "enabled"
  ```

  String interpolation:
  ```yaml
  value: ${metadata.name}-sidecar
  ```

  Structure with embedded CEL:
  ```yaml
  value:
    name: ${parameters.volumeName}
    persistentVolumeClaim:
      claimName: ${metadata.name}-pvc
  ```

  Standalone CEL expression:
  ```yaml
  value: ${configurations.toContainerEnvFrom()}
  ```

## Supported Operations

### add
Adds a value at the specified path. Creates parent maps automatically if they don't exist.

```yaml
# Add a new label
- op: add
  path: /metadata/labels/monitoring
  value: "enabled"

# Append to array
- op: add
  path: /spec/containers/-
  value:
    name: sidecar
    image: sidecar:latest

# Create nested structure (auto-creates parents)
- op: add
  path: /metadata/annotations/example.com~1version
  value: "v2.0"
```

### replace
Replaces an existing value. The path must exist.

```yaml
# Replace a value
- op: replace
  path: /spec/replicas
  value: 3

# Replace array element
- op: replace
  path: /spec/containers/0/image
  value: nginx:latest
```

### remove
Removes a value at the path. No-op if path doesn't exist (idempotent).

```yaml
# Remove a label
- op: remove
  path: /metadata/labels/deprecated

# Remove array element
- op: remove
  path: /spec/containers/1
```

## Array Filtering

Use JSONPath-like syntax to target specific array elements:

### Basic Filtering

```yaml
# Target container by name
- op: add
  path: /spec/template/spec/containers[?(@.name=='app')]/env/-
  value:
    name: MONITORING
    value: enabled

# Target volume by name
- op: replace
  path: /spec/template/spec/volumes[?(@.name=='data')]/emptyDir
  value:
    sizeLimit: 10Gi
```

### Nested Field Filters

```yaml
# Filter by image field, navigate to ports
- op: add
  path: /spec/containers[?(@.image=='nginx:latest')]/ports/-
  value:
    containerPort: 8080

# Filter using nested field path (dot notation)
- op: replace
  path: /spec/containers[?(@.resources.limits.memory=='2Gi')]/image
  value: app:high-mem-v2
```

### Filter Limitations

**Currently supported**: Only simple equality filters of the form `@.field.path=='value'`

```yaml
# Supported - simple field equality
- op: add
  path: /spec/containers[?(@.name=='app')]/env/-
  value:
    name: VERSION
    value: "v2"

# Supported - nested field equality (using dot notation)
- op: add
  path: /spec/volumes[?(@.configMap.name=='app-config')]/configMap/defaultMode
  value: 0644
```

**Not supported**: Multiple conditions (`&&`, `||`), operators like `contains`, array indexing in filters (`@.ports[0]`), or existence checks (`@.ports`).

### Wildcard `[*]`

The `[*]` selector matches **all elements** of an array, expanding the path into one target per element. This is useful when you need to apply a patch across all items without knowing their count or filtering by a field.

```yaml
# Replace a field in every rule
- op: replace
  path: /spec/rules/[*]/host
  value: "new.example.com"

# Append to every rule's backendRefs
- op: add
  path: /spec/rules/[*]/backendRefs/-
  value:
    name: new-backend
    port: 8080
```

Wildcards compose with filters to target nested elements across all parents:

```yaml
# Replace matching backendRefs across ALL rules (not just rules/0)
- op: replace
  path: /spec/rules/[*]/backendRefs/[?(@.name=='${metadata.componentName}')]
  value:
    group: gateway.kgateway.dev
    kind: Backend
    name: ${metadata.componentName}-api-gw-backend
```

Like filters, `[*]` returns an error if the array is empty or the path doesn't point to an array.

## Path Resolution Behavior

OpenChoreo extends RFC 6902 JSON Patch to provide Kubernetes-friendly behavior:

| Path Type | Operation | Behavior | RFC 6902 |
|-----------|-----------|----------|----------|
| **Filter** `[?(...)]` | add, replace, remove | **Error** if selector matches zero elements | Standard |
| **Wildcard** `[*]` | add, replace, remove | **Error** if array is empty or path is not an array | Extended |
| **Map key** | add | **Auto-create** parent maps if missing | Extended |
| **Map key** | replace | **Error** if target doesn't exist | Standard |
| **Map key** | remove | **Idempotent** - no error if key doesn't exist | Extended |
| **Array index** | add, replace, remove | **Error** if index out of bounds | Standard |

### Extensions to RFC 6902

OpenChoreo makes two deliberate extensions to RFC 6902:

1. **Auto-create parent maps** - `add` operations automatically create missing parent objects, reducing boilerplate in Trait patches
2. **Idempotent map key removal** - `remove` operations on map keys succeed silently if the key doesn't exist, useful for cleanup operations

These extensions match Kubernetes Strategic Merge Patch behavior. The map key auto-creation and idempotent removal are similar to using `evanphx/json-patch` with:
- `EnsurePathExistsOnAdd: true`
- `AllowMissingPathOnRemove: true`

**Note on Arrays**: All array index operations (add, replace, remove) error on out-of-bounds indices, as this likely indicates an error in the patch configuration or a mismatch between the patch and the ComponentType output. For dynamic array operations, use filters (e.g., `[?(@.name=='sidecar')]`) instead of positional indices.

### Examples

```yaml
# Filter path - ERRORS if no container named 'app' exists
- op: add
  path: /spec/containers[?(@.name=='app')]/env/-
  value: {name: VAR, value: val}

# Map key path - AUTO-CREATES /spec/monitoring if missing
- op: add
  path: /spec/monitoring/enabled
  value: true

# Map key removal - IDEMPOTENT (no error if key missing)
- op: remove
  path: /metadata/labels/deprecated-feature

# Array index - ERRORS if index out of bounds
- op: add
  path: /spec/containers/2  # Errors if less than 3 containers
  value: {name: sidecar, image: sidecar:v1}

- op: remove
  path: /spec/containers/2  # Errors if less than 3 containers
```

### Comparison with Kubernetes API Server

The Kubernetes API server's JSON Patch implementation strictly follows RFC 6902 and will **error** on both missing parents and missing remove targets. However, Kubernetes users typically use **Strategic Merge Patch** (the default for `kubectl patch`), which auto-creates parents similar to OpenChoreo.

OpenChoreo's behavior is designed for Trait authors who expect Kubernetes-like convenience without needing to write conditional logic for path existence checks.

## Resource Targeting

### Basic Targeting

The `target` spec requires `kind`, `group`, and `version` fields. The `targetPlane` field is optional and defaults to `"dataplane"`:

```yaml
patches:
  # Patch apps/v1 Deployment in dataplane
  - target:
      kind: Deployment   # Required: Resource kind
      group: apps        # Required: API group (use "" for core resources)
      version: v1        # Required: API version
      where: ""          # Optional: CEL expression to filter resources
    targetPlane: dataplane  # Optional: defaults to "dataplane" if not specified
    operations:
      - op: add
        path: /metadata/labels/patched
        value: "true"

  # Patch core v1 Service (note: group is explicitly "")
  - target:
      kind: Service
      group: ""          # Empty string for core API resources
      version: v1
    # targetPlane omitted - defaults to "dataplane"
    operations:
      - op: add
        path: /metadata/annotations/patched
        value: "true"
```

**Key Points:**
- `kind`, `group`, and `version` are **always required**
- For core API resources (Service, ConfigMap, Secret), use `group: ""`
- `targetPlane` is optional and defaults to `"dataplane"` if not specified
- `where` clause is optional for filtering resources

**Design Rationale:**
- **Why `group` is required**: Making `group` required eliminates ambiguity. Empty string `""` has semantic meaning (core API resources like Service, ConfigMap, Secret), so we require explicit specification. This ensures patches target the intended resources; omitting the group could result in not matching any resources at all.
- **Why `targetPlane` defaults to "dataplane"**: Most resources are deployed to the dataplane, with few (if any) on the observability plane. Defaulting to the common case reduces verbosity while allowing explicit specification when needed.

### CEL-Based Filtering

Use `where` clause with CEL expressions to target resources conditionally:

```yaml
patches:
  - target:
      kind: Deployment
      group: apps
      version: v1
      where: ${resource.spec.replicas > 1}  # Only multi-replica deployments
    targetPlane: dataplane
    operations:
      - op: add
        path: /metadata/annotations/ha-mode
        value: "true"

  - target:
      kind: Service
      group: ""          # Core API
      version: v1
      where: ${resource.spec.type == 'LoadBalancer'}
    targetPlane: dataplane
    operations:
      - op: add
        path: /metadata/annotations/external
        value: "true"
```

## ForEach Iteration

Apply patches iteratively over a list:

```yaml
patches:
  - target:
      kind: ConfigMap
      group: ""
      version: v1
    targetPlane: dataplane
    forEach: ${parameters.environments}
    var: env
    operations:
      - op: add
        path: /data/${env.name}
        value: ${env.value}

  - target:
      kind: Deployment
      group: apps
      version: v1
    targetPlane: dataplane
    forEach: ${parameters.extraPorts}
    var: port
    operations:
      - op: add
        path: /spec/template/spec/containers[?(@.name=='app')]/ports/-
        value:
          containerPort: ${port.number}
          name: ${port.name}
```

## RFC 6901 Escaping

JSON Patch uses JSON Pointer (RFC 6901) for path references. The specification **requires** escaping special characters in path segments:

- `~` becomes `~0`
- `/` becomes `~1`

This is particularly important for Kubernetes resource paths that contain these characters (e.g., `kubernetes.io/ingress-class` annotations).

```yaml
# Path with / character (Kubernetes annotation)
- op: add
  path: /metadata/annotations/kubernetes.io~1ingress-class
  value: nginx

# Path with ~ character
- op: add
  path: /data/config~0backup
  value: backup-data

# Complex example with both
- op: add
  path: /metadata/labels/app.kubernetes.io~1managed~0by
  value: openchoreo
```

## Advanced Examples

### Add Sidecar Container

```yaml
apiVersion: v1alpha1
kind: Trait
metadata:
  name: logging-sidecar
spec:
  patches:
    - target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        # Add sidecar container
        - op: add
          path: /spec/template/spec/containers/-
          value:
            name: fluentd
            image: fluent/fluentd:v1.14
            volumeMounts:
            - name: logs
              mountPath: /var/log

        # Add shared volume
        - op: add
          path: /spec/template/spec/volumes/-
          value:
            name: logs
            emptyDir: {}

        # Mount log volume to main container
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/volumeMounts/-
          value:
            name: logs
            mountPath: /app/logs
```

### Modify Service Ports

```yaml
apiVersion: v1alpha1
kind: Trait
metadata:
  name: metrics-port
spec:
  patches:
    - target:
        kind: Service
      operations:
        # Add metrics port to service
        - op: add
          path: /spec/ports/-
          value:
            name: metrics
            port: 9090
            targetPort: metrics
            protocol: TCP

        # Add selector for metrics
        - op: add
          path: /spec/selector/metrics
          value: enabled
```

### Conditional Resource Limits

```yaml
apiVersion: v1alpha1
kind: Trait
metadata:
  name: resource-optimizer
spec:
  schema:
    tier: "string | enum=small,medium,large default=small"

  patches:
    - target:
        group: apps
        version: v1
        kind: Deployment
        where: ${parameters.tier == 'small'}
      operations:
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/limits/memory
          value: 512Mi
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/limits/cpu
          value: 500m
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/requests/memory
          value: 256Mi
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/requests/cpu
          value: 250m

    - target:
        group: apps
        version: v1
        kind: Deployment
        where: ${parameters.tier == 'large'}
      operations:
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/limits/memory
          value: 4Gi
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/limits/cpu
          value: 2000m
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/requests/memory
          value: 2Gi
        - op: add
          path: /spec/template/spec/containers[?(@.name=='${metadata.name}')]/resources/requests/cpu
          value: 1000m
```

### Network Policy Addition

```yaml
apiVersion: v1alpha1
kind: Trait
metadata:
  name: network-isolation
spec:
  patches:
    # First ensure NetworkPolicy exists via 'creates'
    # Then patch it based on configuration
    - target:
        group: networking.k8s.io
        version: v1
        kind: NetworkPolicy
        name: ${metadata.name}-netpol
      operations:
        # Add ingress rules
        - op: add
          path: /spec/ingress/-
          value:
            from:
            - podSelector:
                matchLabels:
                  app: frontend
            ports:
            - protocol: TCP
              port: 8080

        # Add egress rules
        - op: add
          path: /spec/egress/-
          value:
            to:
            - podSelector:
                matchLabels:
                  app: database
            ports:
            - protocol: TCP
              port: 5432
```

## Common Patterns

### Safe Label Addition

```yaml
# Good - adds individual labels without affecting existing ones
- op: add
  path: /metadata/labels/monitoring
  value: enabled
- op: add
  path: /metadata/labels/trait
  value: ${metadata.name}

# Bad - replaces all existing labels
- op: replace
  path: /metadata/labels
  value:
    monitoring: enabled
    trait: ${metadata.name}
```

### Conditional Container Environment

```yaml
# Add environment variables based on configuration
- target:
    group: apps
    version: v1
    kind: Deployment
  forEach: ${parameters.envVars}
  var: envVar
  operations:
    - op: add
      path: /spec/template/spec/containers[?(@.name=='${parameters.containerName}')]/env/-
      value:
        name: ${envVar.name}
        value: ${envVar.value}
```

### Volume Mount Injection

```yaml
# Add volume mounts to specific containers
- op: add
  path: /spec/template/spec/volumes/-
  value:
    name: config
    configMap:
      name: ${metadata.name}-config

- op: add
  path: /spec/template/spec/containers[?(@.name=='app')]/volumeMounts/-
  value:
    name: config
    mountPath: /etc/config
    readOnly: true
```

### Service Mesh Annotations

```yaml
# Add Istio sidecar annotations
- op: add
  path: /spec/template/metadata/annotations/sidecar.istio.io~1inject
  value: "true"
- op: add
  path: /spec/template/metadata/annotations/sidecar.istio.io~1proxyCPU
  value: "100m"
- op: add
  path: /spec/template/metadata/annotations/sidecar.istio.io~1proxyMemory
  value: "128Mi"
```

### Use Filters and Wildcards for Explicit Targeting

```yaml
# Good - explicit container selection
- op: add
  path: /spec/containers[?(@.name=='app')]/env/-
  value: {name: VAR, value: val}

# Good - target all array elements with wildcard
- op: replace
  path: /spec/rules/[*]/backendRefs/[?(@.name=='my-svc')]
  value: {name: my-svc, port: 443}

# Bad - assumes container position
- op: add
  path: /spec/containers/0/env/-
  value: {name: VAR, value: val}
```

### Use Proper Escaping

```yaml
# Good - escaped annotation
- op: add
  path: /metadata/annotations/example.com~1version
  value: v1

# Bad - unescaped will fail
- op: add
  path: /metadata/annotations/example.com/version
  value: v1
```



File: docs/templating/templating.md
---
# Templating

This guide covers the OpenChoreo templating system for dynamic resource generation.

## Overview

OpenChoreo's templating system enables dynamic configuration through expressions embedded in YAML/JSON structures. Expressions are enclosed in `${}` and evaluated using CEL (Common Expression Language). The templating format, helper functions, and YAML integration are OpenChoreo-specific, while CEL is used only for expression evaluation within `${}`.

Key components:
- **Templating Format**: OpenChoreo-specific YAML/JSON structure with embedded expressions
- **Expression Language**: CEL (Common Expression Language) for evaluating expressions inside `${}`
- **Helper Functions**: OpenChoreo-provided functions like `oc_omit()`, `oc_merge()`, and `oc_generate_name()`

The templating engine is generic and can be used with any context variables. This guide demonstrates the engine capabilities using examples from ComponentTypes and Traits.

## Where Expressions Can Be Used

OpenChoreo templates support expressions in three locations:

### 1. Expression as Entire Value (Standalone)

When an expression is the entire value, it returns native CEL types and preserves the original data type.

**YAML Syntax Options:**
```yaml
# Without quotes (simplest)
replicas: ${parameters.replicas}

# With quotes (same result, useful for YAML compatibility)
replicas: "${parameters.replicas}"

# With block scalar | (useful to avoid escaping issues with complex expressions)
replicas: |
  ${parameters.replicas > 0 ? parameters.replicas : 1}
```

**Examples:**
```yaml
# Returns an integer
replicas: ${parameters.replicas}

# Returns a map
labels: ${metadata.labels}

# Returns a boolean
enabled: ${has(parameters.feature) ? parameters.feature : false}

# Returns a list
volumes: ${parameters.volumes}

# Complex expression with block scalar (avoids escaping quotes in YAML)
nodeSelector: |
  ${parameters.highPerformance ? {"node-type": "compute"} : {"node-type": "standard"}}
```

### 2. Expression as Part of String Value (Interpolated)

When an expression is embedded within a string, it is automatically converted to a string and interpolated.

```yaml
# String interpolation - multiple expressions
message: "Application ${metadata.name} has ${parameters.replicas} replicas"

# URL construction
url: "https://${metadata.name}.${metadata.namespace}.svc.cluster.local:${parameters.port}"

# Image tag
image: "${parameters.registry}/${parameters.repository}:${parameters.tag}"

# Note: Single expression in quotes is still standalone (not interpolated)
# These are equivalent - both preserve integer type:
replicas: ${parameters.replicas}
replicas: "${parameters.replicas}"
```

### 3. Expression as Map Key (Dynamic Keys)

Map keys can be dynamically generated using expressions (must evaluate to strings).

```yaml
# Dynamic service port mapping
services:
  ${metadata.serviceName}: 8080
  ${metadata.name + "-metrics"}: 9090

# Dynamic labels with concatenation
labels:
  ${'app.kubernetes.io/' + metadata.name}: active
  ${parameters.labelPrefix + '/version'}: ${parameters.version}
```

## CEL Capabilities

### Map Access Notation

Both dot notation and bracket notation work for accessing map fields:

```yaml
# These are equivalent for static keys:
${workload.container.image}
${configurations.configs.envs}
```

Bracket notation is **required** for:
- **Dynamic keys** (variables): `${workload.endpoints[parameters.endpointName].port}`
- **Keys with special characters**: `${resource.metadata.labels["app.kubernetes.io/name"]}`
- **Optional dynamic keys**: `${workload.endpoints[?parameters.endpointName].?port.orValue(8080)}`

### Membership and Existence Checks

The `in` operator checks membership in maps and lists:

```
# Check if a key exists in a map
parameters.endpointName in workload.endpoints

# Check if a value exists in a list (primitives only — strings, ints, bools)
"HTTP" in parameters.allowedTypes
```

For maps, `exists()` and `all()` iterate over **keys** — use bracket notation to access values:

```
# Check if any endpoint is of type HTTP
workload.endpoints.exists(name, workload.endpoints[name].type == 'HTTP')

# Check all endpoints have a port > 0
workload.endpoints.all(name, workload.endpoints[name].port > 0)
```

### Conditional Logic

```yaml
# Service type with default
serviceType: ${has(parameters.serviceType) ? parameters.serviceType : "ClusterIP"}

# Replicas with minimum
replicas: ${parameters.replicas > 0 ? parameters.replicas : 1}

# Conditional string value
status: ${parameters.enabled ? "active" : "inactive"}

# Multi-condition logic
nodeSelector: |
  ${parameters.highPerformance ?
    {"node-type": "compute-optimized"} :
    (parameters.costOptimized ?
      {"node-type": "spot"} :
      {"node-type": "general-purpose"})}

# Conditional resource limits
resources: |
  ${parameters.resourceTier == "small" ? {
      "limits": {"memory": "512Mi", "cpu": "500m"},
      "requests": {"memory": "256Mi", "cpu": "250m"}
    } : (parameters.resourceTier == "medium" ? {
      "limits": {"memory": "2Gi", "cpu": "1000m"},
      "requests": {"memory": "1Gi", "cpu": "500m"}
    } : {
      "limits": {"memory": "4Gi", "cpu": "2000m"},
      "requests": {"memory": "2Gi", "cpu": "1000m"}
    })}
```

### Safe Navigation

```yaml
# Optional chaining with ? for static keys
customValue: ${parameters.?custom.?value.orValue("default")}

# Optional index access with dynamic keys
endpointConfig: ${workload.endpoints[?parameters.endpointName].?port.orValue(8080)}

# Map with optional keys (entire map must be inside CEL expression)
config: |
  ${{"required": parameters.requiredConfig, ?"optional": parameters.?optionalConfig}}
```

### Array and List Operations

```yaml
# Transform list of key-value pairs to environment variables
env: |
  ${parameters.envVars.map(e, {"name": e.key, "value": e.value})}

# Filter and transform
ports: |
  ${parameters.services.filter(s, s.enabled).map(s, {"port": s.port, "name": s.name})}

# List operations
firstItem: ${parameters.items[0]}
lastItem: ${parameters.items[size(parameters.items) - 1]}
joined: ${parameters.items.join(",")}

# Sorting lists
sortedStrings: ${parameters.names.sort()}                        # sort primitive lists (strings, ints, etc.)
sortedByName: ${parameters.items.sortBy(item, item.name)}        # sort object lists by a field

# List concatenation
combined: ${parameters.list1 + parameters.list2}
withInlineItem: ${parameters.userPorts + [{"port": 8080, "name": "http"}]}

# Flatten nested lists
flattened: ${[[1, 2], [3, 4]].flatten()}  # returns [1, 2, 3, 4]

# Flatten with depth limit
partial: ${[[1, [2, 3]], [4]].flatten(1)}  # returns [1, [2, 3], 4]

# Flatten combined with transformList - useful for iterating over all items
# across multiple containers/groups
allFiles: |
  ${configurations.transformList(containerName, cfg,
    has(cfg.files) ? cfg.files.map(f, {
      "container": containerName,
      "name": f.name
    }) : []
  ).flatten()}
```

### Map Operations

```yaml
# Transform map to list using transformList
endpointList: |
  ${workload.endpoints.transformList(name, ep, {
    "name": name,
    "port": ep.port
  })}

# Transform list to map with dynamic keys
envMap: |
  ${parameters.envVars.transformMapEntry(i, v, {v.name: v.value})}

# Map transformation (map to map)
labelMap: |
  ${parameters.labels.transformMap(k, v, {"app/" + k: v})}

# Filtered map (filter first, then transform to map)
activeServices: |
  ${parameters.services.filter(s, s.enabled)
    .transformMapEntry(i, s, {s.name: s.port})}
```

### String Operations

```yaml
# String manipulation
uppercaseName: ${metadata.name.upperAscii()}
trimmedValue: ${parameters.value.trim()}
replaced: ${parameters.text.replace("old", "new")}
prefixed: ${parameters.value.startsWith("prefix")}

# Split string into list
parts: ${parameters.path.split("/")}                    # "/a/b/c" → ["", "a", "b", "c"]
limited: ${parameters.text.split(",", 2)}               # "a,b,c" → ["a", "b,c"]

# Extract substring
suffix: ${parameters.name.substring(4)}                 # "hello-world" → "o-world"
middle: ${parameters.name.substring(0, 5)}              # "hello-world" → "hello"
```

### Math Operations

```yaml
# Mathematical operations
maxValue: ${math.greatest([parameters.min, parameters.max, parameters.default])}
minValue: ${math.least([parameters.v1, parameters.v2, parameters.v3])}
rounded: ${math.ceil(parameters.floatValue)}
```

### Encoding Operations

```yaml
# Base64 encode a string (must convert to bytes first)
encoded: ${base64.encode(bytes(parameters.value))}

# Base64 decode to bytes, then convert to string
decoded: ${string(base64.decode(parameters.encodedValue))}
```

## Built-in Functions

### oc_omit()

Removes fields from output. Has two distinct behaviors depending on usage:

**1. Field-level omission** - Removes the YAML key from the template:

```yaml
# Omit individual fields
resources:
  limits:
    memory: ${parameters.memoryLimit}
    cpu: ${has(parameters.cpuLimit) ? parameters.cpuLimit : oc_omit()}
    # When cpuLimit is missing, the entire 'cpu:' line is removed

# Omit entire nested maps
metadata:
  name: ${metadata.name}
  annotations: ${has(parameters.annotations) ? parameters.annotations : oc_omit()}
  # When annotations is missing, the entire 'annotations:' key is removed
```

**2. Expression-level omission** - Removes keys from within a CEL map expression:

```yaml
# Use CEL's optional key syntax for simple optional fields
container: |
  ${{
    "image": parameters.image,
    ?"cpu": parameters.?cpu,
    ?"memory": parameters.?memory
  }}
  # Keys are only included if the value exists

# Use oc_omit() when conditional logic is involved
container: |
  ${{
    "image": parameters.image,
    "cpu": parameters.cpuLimit > 0 ? parameters.cpuLimit : oc_omit(),
    "debug": parameters.environment == "dev" ? true : oc_omit()
  }}
  # Keys are conditionally included based on logic, not just existence
```

### oc_merge(base, override, ...)
Shallow merge two or more maps (later maps override earlier ones):

```yaml
# Merge default and custom labels
labels: |
  ${oc_merge({"app": metadata.name, "version": "v1"}, parameters.customLabels)}

# Merge multiple maps
config: ${oc_merge(defaults, layer1, layer2, layer3)}
```

### oc_generate_name(...args)
Convert arguments to valid Kubernetes resource names (max 253 chars) with a hash suffix for uniqueness:

```yaml
# Create valid ConfigMap name with hash
name: ${oc_generate_name(metadata.name, "config", parameters.environment)}
# Result: "myapp-config-prod-a1b2c3d4" (lowercase, alphanumeric, hyphens + 8-char hash)

# Handle special characters and add hash
name: ${oc_generate_name("My_App", "Service!")}
# Result: "my-app-service-e5f6g7h8"

# Single argument also gets hash
name: ${oc_generate_name("Hello World!")}
# Result: "hello-world-7f83b165"
```

**Note:** The function always appends an 8-character hash suffix to ensure uniqueness. The hash is generated from the original input values, so the same inputs will always produce the same output.

### oc_dns_label(...args)
Same as `oc_generate_name` but enforces a 63-character limit, suitable for DNS label names (e.g., hostname subdomains in HTTPRoute). The hash suffix still guarantees uniqueness even after truncation:

```yaml
# Generate a hostname subdomain label (≤63 chars) for webapp HTTPRoutes
hostnames:
  - ${oc_dns_label(endpointName, metadata.componentName, metadata.environmentName, metadata.componentNamespace)}.${gateway.ingress.external.https.host}
# Result subdomain: "my-endpoint-my-service-dev-a1b2c3d4" (truncated to ≤63 chars if needed)
```

Use `oc_dns_label` when the name appears as a hostname subdomain (RFC 1123 label, max 63 chars). Use `oc_generate_name` for all other Kubernetes resource names.

## OpenChoreo Resource Control Fields

OpenChoreo extends the templating system with special fields for dynamic resource generation:

### includeWhen - Conditional Resource Inclusion (ComponentType and Trait creates)

The `includeWhen` field on ComponentType resources and Trait creates controls whether a resource is included in the output based on a CEL expression:

```yaml
# In ComponentType
resources:
  # Only create HPA if auto-scaling is enabled
  - includeWhen: ${parameters.autoscaling.enabled}
    resource:
      apiVersion: autoscaling/v2
      kind: HorizontalPodAutoscaler
      metadata:
        name: ${metadata.name}
      spec:
        scaleTargetRef:
          apiVersion: apps/v1
          kind: Deployment
          name: ${metadata.name}
        minReplicas: ${parameters.autoscaling.minReplicas}
        maxReplicas: ${parameters.autoscaling.maxReplicas}

  # Create PDB only for production with multiple replicas
  - includeWhen: ${parameters.environment == "production" && parameters.replicas > 1}
    resource:
      apiVersion: policy/v1
      kind: PodDisruptionBudget
      metadata:
        name: ${metadata.name}
      spec:
        minAvailable: ${parameters.replicas - 1}
        selector:
          matchLabels: ${metadata.podSelectors}
```

### forEach - Dynamic Resource Generation (ComponentType, Trait creates, and Trait patches)

The `forEach` field generates multiple resources from a list or map. Available on ComponentType resources, Trait creates, and Trait patches.

- **Lists**: Each item is bound directly to the loop variable
- **Maps**: Each item has `.key` and `.value` fields; keys are iterated in **alphabetical order** for deterministic output

```yaml
resources:
  # Generate ConfigMaps for each database
  - forEach: ${parameters.databases}
    var: db
    resource:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${oc_generate_name(metadata.name, db.name, "config")}
      data:
        host: ${db.host}
        port: ${string(db.port)}
        database: ${db.database}

  # Create Services for each exposed port
  - forEach: ${parameters.exposedPorts}
    var: portConfig
    resource:
      apiVersion: v1
      kind: Service
      metadata:
        name: ${oc_generate_name(metadata.name, portConfig.name)}
      spec:
        selector: ${metadata.podSelectors}
        ports:
        - port: ${portConfig.port}
          targetPort: ${portConfig.targetPort}
          name: ${portConfig.name}
```

### Filtering Items in forEach

**Use `.filter()` within the forEach expression to iterate only over matching items:**

```yaml
resources:
  # Generate secrets only for enabled integrations
  - forEach: ${parameters.integrations.filter(i, i.enabled && has(i.credentials))}
    var: integration
    resource:
      apiVersion: v1
      kind: Secret
      metadata:
        name: ${oc_generate_name(metadata.name, integration.name, "secret")}
      type: Opaque
      stringData:
        api_key: ${integration.credentials.apiKey}
        api_secret: ${integration.credentials.apiSecret}

  # Create Services only for exposed ports
  - forEach: ${parameters.ports.filter(p, p.expose)}
    var: port
    resource:
      apiVersion: v1
      kind: Service
      metadata:
        name: ${oc_generate_name(metadata.name, port.name)}
      spec:
        ports:
          - port: ${port.port}
            name: ${port.name}
```

**You can chain `.filter()`, `.map()`, and other CEL list operations:**

```yaml
resources:
  # Filter enabled items, transform, then iterate
  - forEach: |
      ${parameters.configs
        .filter(c, c.enabled)
        .map(c, {"name": c.name, "data": c.value})}
    var: config
    resource:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${config.name}
      data:
        value: ${config.data}
```

### Combining forEach with includeWhen

**Important:** `includeWhen` is evaluated **before** the forEach loop starts and controls whether the **entire forEach block** is included. The loop variable is **not available** in `includeWhen` expressions.

```yaml
resources:
  # includeWhen controls entire forEach block - not individual items
  - includeWhen: ${parameters.createSecrets}
    forEach: ${parameters.integrations}
    var: integration
    resource:
      apiVersion: v1
      kind: Secret
      metadata:
        name: ${integration.name}

  # WRONG - loop variable not available in includeWhen
  - includeWhen: ${integration.enabled}  # ERROR: 'integration' doesn't exist yet
    forEach: ${parameters.integrations}
    var: integration
    resource:
      apiVersion: v1
      kind: Secret
      metadata:
        name: ${integration.name}

  # CORRECT - use filter() for item-level filtering
  - forEach: ${parameters.integrations.filter(i, i.enabled)}
    var: integration
    resource:
      apiVersion: v1
      kind: Secret
      metadata:
        name: ${integration.name}
```

### Using forEach with Maps

When iterating over a map, each item has `.key` and `.value` fields. **Map keys are iterated in alphabetical order** to ensure deterministic resource generation across runs.

```yaml
resources:
  # Generate ConfigMap from map entries
  # If configFiles = {"database": "postgres://...", "cache": "redis://..."}
  # Items are iterated in order: cache, database (alphabetically sorted)
  - forEach: ${parameters.configFiles}
    var: config
    resource:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${oc_generate_name(metadata.name, config.key)}
      data:
        "${config.key}": ${config.value}
```

**Accessing nested values in maps:**

```yaml
resources:
  # Map with complex values
  # connections = {"db": {"host": "localhost", "port": 5432}, "cache": {"host": "redis", "port": 6379}}
  - forEach: ${parameters.connections}
    var: conn
    resource:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: ${conn.key}-config
      data:
        host: ${conn.value.host}
        port: "${string(conn.value.port)}"
```

**Empty maps produce zero iterations** (no resources generated).

### Usage in Traits

Trait patches support `forEach` for iteration (over lists or maps) and `where` for conditional targeting:

```yaml
# In Trait definition
apiVersion: v1alpha1
kind: Trait
metadata:
  name: monitoring
spec:
  creates:
    # Trait creates support includeWhen and forEach (same as ComponentType resources)
    # Simple unconditional resource
    - template:
        apiVersion: monitoring.coreos.com/v1
        kind: ServiceMonitor
        metadata:
          name: ${metadata.name}
        spec:
          selector:
            matchLabels: ${metadata.podSelectors}

    # Use includeWhen for conditional resource creation
    - includeWhen: ${parameters.alerting.enabled}
      template:
        apiVersion: monitoring.coreos.com/v1
        kind: PrometheusRule
        metadata:
          name: ${metadata.name}-alerts
        spec:
          groups:
            - name: ${metadata.name}
              rules: ${parameters.alerting.rules}

    # Use forEach for generating multiple resources
    - forEach: ${parameters.volumes}
      var: vol
      template:
        apiVersion: v1
        kind: PersistentVolumeClaim
        metadata:
          name: ${oc_generate_name(metadata.name, vol.name)}
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: ${vol.size}

    # Combine includeWhen and forEach - includeWhen controls the entire block
    - includeWhen: ${parameters.createSecrets}
      forEach: ${parameters.secrets}
      var: secret
      template:
        apiVersion: v1
        kind: Secret
        metadata:
          name: ${oc_generate_name(metadata.name, secret.name)}
        type: Opaque
        stringData: ${secret.data}

  patches:
    # Use 'where' in target for conditional patching
    - target:
        group: apps
        version: v1
        kind: Deployment
        where: ${parameters.monitoring.enabled}
      operations:
        - op: add
          path: /spec/template/metadata/annotations/prometheus.io~1scrape
          value: "true"

    # Use forEach for iterating over lists
    - forEach: ${parameters.extraPorts}
      var: port
      target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: add
          path: /spec/template/spec/containers/0/ports/-
          value: |
            ${{"containerPort": port.number, "name": port.name}}

    # Use forEach with maps - keys are iterated alphabetically
    - forEach: ${parameters.envVars}
      var: env
      target:
        group: apps
        version: v1
        kind: Deployment
      operations:
        - op: add
          path: /spec/template/spec/containers/0/env/-
          value:
            name: ${env.key}
            value: ${env.value}
```



File: docs/templating/validations.md
---
# Validation Rules

This guide covers CEL-based validation rules for ComponentTypes and Traits.

## Overview

Validation rules enforce semantic constraints that JSON Schema alone cannot express. While schemas define data shape (types, ranges, required fields), validation rules express cross-field relationships, conditional requirements, and domain-specific invariants.

Rules are CEL expressions wrapped in `${...}` that must evaluate to `true`. When a rule evaluates to `false`, the associated message is surfaced as an error. All rules are evaluated (no short-circuiting), so multiple failures are reported together.

Validation rules run **after** schema defaults are applied and **before** resource rendering begins.

## Rule Structure

Validation rules are defined in the `spec.validations` field of ComponentTypes and Traits:

```yaml
validations:
  - rule: "${size(workload.endpoints) > 0}"
    message: "must expose at least one endpoint"
  - rule: "${environmentConfigs.maxReplicas >= environmentConfigs.minReplicas}"
    message: "maxReplicas must be greater than or equal to minReplicas"
```

| Field | Required | Description |
|-------|----------|-------------|
| `rule` | Yes | CEL expression wrapped in `${...}` that must evaluate to `true` |
| `message` | Yes | Error message shown when the rule evaluates to `false` |

Rules are validated at admission time: the CEL expression must parse correctly and return a boolean type. Invalid expressions are rejected before the resource is created.

## Context Variables

Validation rules have access to the same context variables as resource templates:

| CRD | Context Type | Available Variables |
|-----|-------------|---------------------|
| ComponentType | ComponentContext | `metadata`, `parameters`, `environmentConfigs`, `dataplane`, `workload`, `configurations` |
| Trait | TraitContext | `metadata`, `parameters`, `environmentConfigs`, `dataplane`, `trait`, `workload`, `configurations` |

See [Template Context Variables](./context.md) for full documentation of each variable.

## Examples

### Differentiating deployment subtypes

```yaml
# deployment/worker - must NOT expose endpoints
kind: ComponentType
metadata:
  name: worker
spec:
  workloadType: deployment
  validations:
    - rule: "${size(workload.endpoints) == 0}"
      message: "A deployment/worker must not expose endpoints. Use deployment/service instead."
```

```yaml
# deployment/service - MUST expose at least one endpoint
kind: ComponentType
metadata:
  name: service
spec:
  workloadType: deployment
  validations:
    - rule: "${size(workload.endpoints) > 0}"
      message: "A deployment/service must expose at least one endpoint."
```

```yaml
# deployment/web-app - MUST expose at least one HTTP endpoint
kind: ComponentType
metadata:
  name: web-app
spec:
  workloadType: deployment
  validations:
    - rule: "${workload.endpoints.exists(name, workload.endpoints[name].type == 'HTTP')}"
      message: "A deployment/web-app must expose at least one HTTP endpoint."
```

### Trait parameter-to-workload validation

```yaml
# Validates that the referenced endpoint exists and is a WebSocket endpoint
kind: Trait
metadata:
  name: websocket-config
spec:
  parameters:
    openAPIV3Schema:
      endpointName: "string"
  environmentConfigs:
    openAPIV3Schema:
      maxConnectionsPerPod: "integer | default=1000"
  validations:
    - rule: "${parameters.endpointName in workload.endpoints && workload.endpoints[parameters.endpointName].type == 'Websocket'}"
      message: "The specified endpointName must refer to an existing Websocket endpoint."
```

### Cross-field parameter validation

```yaml
# Ensure max >= min for autoscaling
kind: ComponentType
metadata:
  name: autoscaled-service
spec:
  workloadType: deployment
  validations:
    - rule: "${size(workload.endpoints) > 0}"
      message: "Must expose at least one endpoint."
    - rule: "${environmentConfigs.maxReplicas >= environmentConfigs.minReplicas}"
      message: "maxReplicas must be greater than or equal to minReplicas."
  environmentConfigs:
    openAPIV3Schema:
      minReplicas: "integer | default=1 | minimum=1"
      maxReplicas: "integer | default=3 | minimum=1"
```

## Error Messages

When validation rules fail, error messages include the rule index, rule text, and the user-provided message:

```
component type validation failed: rule[0] "${size(workload.endpoints) > 0}" evaluated to false: A deployment/service must expose at least one endpoint.
```

| Scenario | Format |
|----------|--------|
| Rule evaluates to `false` | `rule[i] "rule text" evaluated to false: message` |
| Rule evaluation error | `rule[i] "rule text" evaluation error: ...` |
| Rule returns non-boolean | `rule[i] "rule text" must evaluate to boolean, got T` |

Multiple failures from the same `validations` list are joined with `; `.

## Evaluation Order

1. Schema defaults are applied to parameters and environmentConfigs
2. **ComponentType validation rules** are evaluated using the full ComponentContext
3. Base resources are rendered from ComponentType templates
4. For each trait:
   a. Trait context is built with trait-specific parameters and environmentConfigs
   b. **Trait validation rules** are evaluated using the TraitContext
   c. Trait creates and patches are processed

If any validation rule fails, rendering stops and the error is reported.



File: GOVERNANCE.md
---
# OpenChoreo Governance

This document describes the governance model for the OpenChoreo project. OpenChoreo is a Cloud Native Computing Foundation (CNCF) Sandbox project and follows CNCF project governance principles and the CNCF Code of Conduct.

## Mission

OpenChoreo is an open-source, Kubernetes-native Developer Platform focused on providing clear architectural and development abstractions that reduce developer cognitive load while preserving strong governance, extensibility, and operational clarity for platform teams.

The project aims to:

- Provide composable, Kubernetes-native abstractions for building developer platforms
- Encourage open collaboration and vendor-neutral governance
- Foster a welcoming, inclusive, and sustainable community

## CNCF Alignment

OpenChoreo is a CNCF Sandbox project and operates in alignment with:

- CNCF Code of Conduct
- CNCF Trademark Guidelines
- CNCF Project Lifecycle and Governance guidelines

While OpenChoreo was initially created by contributors from WSO2, it is a vendor-neutral open source project. Governance decisions are made collectively by the maintainer group and are not controlled by any single organization.

## Roles and Responsibilities

### Maintainers

Maintainers have write access to the OpenChoreo GitHub repositories and are responsible for the overall health, direction, and sustainability of the project. A list of current maintainers is maintained in the [MAINTAINERS.md](./MAINTAINERS.md) file.

Maintainer responsibilities include:

- Defining and evolving the project roadmap and architecture
- Reviewing and approving code and documentation changes
- Ensuring consistency with architectural and design principles
- Managing releases and versioning
- Upholding the CNCF Code of Conduct
- Supporting and mentoring contributors

Being a maintainer is a privilege that comes with responsibility. Maintainers are expected to act in the best interests of the project and its community.

### Contributors

Contributors are anyone who participates in the project through code contributions, documentation, issue reporting, reviews, design discussions, or community support.

All contributors are encouraged to:

- Submit issues and pull requests
- Participate in technical and design discussions
- Review code and documentation
- Help other community members

No formal approval is required to become a contributor.

## Decision Making

OpenChoreo follows a consensus-driven decision-making model inspired by other CNCF projects.

### Lazy Consensus

Most day-to-day decisions are made using lazy consensus. Proposals are considered accepted if no substantive objections are raised within a reasonable time period (typically 3–5 business days).

### Voting

Formal votes are used when consensus cannot be reached or when required for specific governance decisions.

Voting rules:

- One vote per maintainer
- Votes may be conducted asynchronously via GitHub issues, pull requests, or mailing lists

A formal vote is required for:

- Adding new maintainers
- Removing maintainers
- Major architectural or governance changes

## Becoming a Maintainer

New maintainers are selected based on demonstrated merit and sustained contributions to the project. Typical criteria include:

- Sustained and meaningful contributions over time (code, documentation, design discussions, or reviews)
  - perform reviews for at least 10 non-trivial PRs
  - contribute at least 20 non-trivial PRs and have them merged
- Demonstrated technical leadership and architectural understanding
- Active participation in project discussions and reviews
- Familiarity with project workflows, contribution guidelines, and quality standards
- A track record of constructive collaboration within the community

A new maintainer must be nominated by an existing maintainer and approved by a **supermajority (at least two-thirds)** of the current maintainers.

## Removing a Maintainer

Maintainers may step down voluntarily at any time.

A maintainer may be removed due to:

- Prolonged inactivity (typically six months or more without meaningful participation, unless a planned return is communicated)
- Repeated failure to meet maintainer responsibilities
- Violation of the CNCF Code of Conduct
- Actions detrimental to the project or community

Removal requires approval by a **supermajority** of the remaining maintainers.

## Meetings

Where feasible, maintainers are encouraged to participate in public community meetings, office hours, or maintainer syncs.

Closed meetings may be held to address security issues or Code of Conduct matters. All maintainers, except those directly involved in a reported Code of Conduct issue, must be invited to such meetings.

## Code of Conduct

OpenChoreo adopts the CNCF Code of Conduct. All participants are expected to adhere to it in all project spaces.

## Security

Security vulnerabilities should be reported privately following the process described in [SECURITY.md](./SECURITY.md).

## Amendments

Changes to this governance document require:

- A pull request proposing the change
- Approval by a **supermajority** of maintainers

## Acknowledgements

This governance model is inspired by governance documents from other CNCF Sandbox and Incubating projects and is intentionally lightweight to support the project’s current stage while allowing room to evolve as the community grows.



File: README.md
---
<div align="left">
  <p></p><p></p>
  <p>
    <img 
    src="./docs/images/openchoreo-horizontal-color.png" alt="OpenChoreo Platform Abstractions" 
    width="600"/>
  </p>
  <h1 style="font-size: 1.5em;">
    A complete, open-source developer platform for Kubernetes
  </h1>
  <p>OpenChoreo is a developer platform for Kubernetes offering development and architecture abstractions, a Backstage-powered developer portal, application CI/CD, GitOps, and observability.</P>

<!-- License & Community -->
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fopenchoreo%2Fopenchoreo.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fopenchoreo%2Fopenchoreo?ref=badge_shield)
[![CNCF Sandbox](https://img.shields.io/badge/CNCF-Sandbox-00ADD8?logo=cloud-native-computing-foundation&logoColor=white)](https://www.cncf.io/projects/openchoreo/)
[![Twitter Follow](https://img.shields.io/twitter/follow/openchoreo?style=social)](https://x.com/openchoreo)
[![Slack](https://img.shields.io/badge/slack-openchoreo-blue?logo=slack)](https://cloud-native.slack.com/archives/C0ABYRG1MND)

<!-- Security & Compliance -->
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/11819/badge)](https://www.bestpractices.dev/projects/11819)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/openchoreo/openchoreo/badge)](https://scorecard.dev/viewer/?uri=github.com/openchoreo/openchoreo)
[![CLOMonitor](https://img.shields.io/endpoint?url=https://clomonitor.io/api/projects/cncf/openchoreo/badge)](https://clomonitor.io/projects/cncf/openchoreo)
[![LFX Health Score](https://insights.linuxfoundation.org/api/badge/health-score?project=openchoreo)](https://insights.linuxfoundation.org/project/openchoreo)

<!-- Build, Quality & Project Info -->
[![Build and Test](https://github.com/openchoreo/openchoreo/actions/workflows/build-and-test.yml/badge.svg?branch=main)](https://github.com/openchoreo/openchoreo/actions/workflows/build-and-test.yml)
[![Codecov](https://codecov.io/gh/openchoreo/openchoreo/branch/main/graph/badge.svg)](https://codecov.io/gh/openchoreo/openchoreo)
[![Go Report Card](https://goreportcard.com/badge/github.com/openchoreo/openchoreo)](https://goreportcard.com/report/github.com/openchoreo/openchoreo)
[![GitHub Release](https://img.shields.io/github/v/release/openchoreo/openchoreo)](https://github.com/openchoreo/openchoreo/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/openchoreo/openchoreo.svg)](https://github.com/openchoreo/openchoreo/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/openchoreo/openchoreo.svg)](https://github.com/openchoreo/openchoreo/issues)
</div>

## Why OpenChoreo?
Kubernetes gives you powerful primitives like Namespaces, Deployments, CronJobs, Services and NetworkPolicies—but they are too low-level for most developers.

Platform engineers are left to build the actual platform: defining higher-level abstractions and wiring together tools for engineering, delivery, security and visibility.

OpenChoreo fills that gap and provides all the essential building blocks of an IDP, including CI, GitOps, observability, RBAC and analytics.

OpenChoreo was originally developed by [WSO2](https://wso2.com), based on its experience building the SaaS internal developer platform formerly known as WSO2 Choreo (now WSO2 Developer Platform), bringing its core ideas to the open-source community.

## OpenChoreo concepts
At its core, OpenChoreo provides a control plane that sits on top of one or more Kubernetes clusters, turning them into a cohesive internal developer platform. 

OpenChoreo introduces a combination of platform abstractions and application abstractions, enabling platform engineers to define standards and enforce policies while giving developers a simplified, self-service experience.

Platform engineers use the following abstractions to create their internal developer platform:
<div align="left">
  <img src="./docs/images/openchoreo-platform-abstractions.png" alt="OpenChoreo Platform Abstractions" width="800"/>
</div>
</br>

- **Namespace**
  - A logical grouping of users and resources, typically aligned to a company, business unit, or team. 
- **Data Plane**
  - A Kubernetes cluster to host one or more of your deployment environments.
- **Environment**
  - A runtime context (e.g., dev, test, staging, prod) where workloads are deployed and executed.
- **Deployment Pipeline**
  - A defined process that governs how workloads are promoted across environments.

</br>

Project managers, architects, and developers use the following abstractions to manage the organization of their work:
<div align="left">
  <img src="./docs/images/openchoreo-development-abstractions.png" alt="OpenChoreo Development Abstractions" width="800"/>
</div>
</br>

These abstractions align with the Domain-Driven Design principles, where projects represent bounded contexts and components represent the individual services or workloads within a domain. Developers use these abstractions to describe the structure and intent of the application in a declarative manner without having to deal with runtime infrastructure details. 

- **Project**
  - A cloud-native application composed of multiple components. Serves as the unit of isolation.
  - Maps to a set of Namespaces (one per Environment) in one or more Data planes.
- **Component**
  - A deployable unit within a project, such as a web service, API, worker, or scheduled task.
  - Maps to workload resources like Deployment, Job, or StatefulSet.
- **Endpoint**
  - A network-accessible interface exposed by a component, including routing rules, supported protocols, and visibility scopes (e.g., public, organization, project).
  - Maps to HTTPRoute (for HTTP), Service resources, and routes via shared ingress gateways. Visibility is enforced via Cilium network policies.
- **Connection**
  - An outbound service dependency defined by a component, targeting either other components or external systems.
  - Maps to Cilium network policies and is routed through egress gateways.

</br>

Architects and developers use the following runtime abstractions to manage how components and projects operate at runtime:
<div align="left">
  <img src="./docs/images/openchoreo-cell-runtime-view.png" alt="OpenChoreo Runtime view of a Project" width="600"/>
</div>
</br>

At runtime, OpenChoreo turns each Project (Bounded Context) into a Cell - a secure, isolated, and observable unit that enforces domain boundaries through infrastructure. 

- **Cell** 
  - A Cell is the runtime reification of a single project in OpenChoreo. It encapsulates all components of a project and controls how they communicate internally and externally through well-defined ingress and egress paths.
  - Communication between components in the same cell is permitted without interception.
  - Cilium and eBPF are used to enforce fine-grained network policies across all ingress and egress paths.
- **Northbound Ingress**
  - Routes incoming traffic from external (internet) sources into the cell.  
  - Endpoints with `visibility: public` are exposed through this ingress path.
- **Southbound Egress**
  - Handles outbound Internet access from components in the Cell. Connections to external services are routed through this egress path. 
- **Westbound Ingress**
  - Handles traffic entering the Cell from within the organization, be it from another cell or just from the internal network. 
- **Eastbound Egress**
  - Handles outbound traffic to other cells or to the internal network.

## OpenChoreo benefits
These abstractions provide the following benefits for businesses to build & operate cloud-native applications:

<div align="left">
  <img src="./docs/images/openchoreo-ddd-to-cell-mapping.png" alt="OpenChoreo DDD-to-Cell Mapping" width="800"/>
</div>
</br>

- **Design clarity for cloud-native applications**
  - OpenChoreo’s abstractions—Projects, Components, Endpoints, and Connections—enable teams to model systems around business domains. 
  - These abstractions align with Domain-Driven Design (DDD) and promote modular, independently deployable services with explicit service boundaries.
- **A developer experience that hides the infrastructure**
  - Developers define application intent (e.g., deploy a component, expose an endpoint, connect to another service) through high-level abstractions. 
  - OpenChoreo compiles this model into the necessary Kubernetes resources, network policies, gateways, and observability hooks.
- **Built-in ingress and egress API management**
  - OpenChoreo manages ingress and egress for all Components based on endpoint visibility (public, organization, or project). 
  - APIs are exposed through kgateways with built-in support for routing, rate limiting, authentication, and traffic policies — without requiring manual configuration.
- **Software catalog and discoverability**
  - All exposed APIs, events and data are automatically registered in an internal catalog. Metadata such as endpoint path, visibility, and owning project is included. 
  - This enables discovery and governance of service interfaces across teams and environments.
- **Zero trust security by default**
  - Each Cell acts as a security boundary where communication between components is explicitly declared and enforced. 
  - Internal and external traffic is governed by Cilium network policies and routed through kgateways. All traffic, including intra-cell communication, is encrypted using mTLS. 
  - No implicit trust is granted — every access is authenticated, authorized, and policy-checked.
- **Observability by default**
  - Each Cell is instrumented for logging, metrics, and distributed tracing. Observability spans all ingress/egress gateways and component-to-component communication, with no additional configuration required. 
  - Collected data can be integrated into existing monitoring and analysis pipelines.
- **Developer and platform separation of concerns**
  - The platform team defines the rules (networking, security, observability, and operational policies). Application teams work within those boundaries by modeling their systems using OpenChoreo abstractions. 
  - This separation ensures consistency, security, and operational reliability at scale.

## How does it work?
In this section, we explain how the OpenChoreo abstractions for platform engineering, code & team organization, software architecture, software engineering and operations are mapped to Kubernetes abstractions and a set of CNCF and other tools that are used to ensure the higher-level abstractions are properly maintained.

<div align="left">
  <img src="./docs/images/openchoreo-architecture-diagram.png" alt="OpenChoreo Architecture" width="800"/>
</div>
</br>

## Getting Started

The easiest way to try OpenChoreo is by following the **[Quick Start Guide](https://openchoreo.dev/docs/getting-started/quick-start-guide/)**. It walks you through setting up Choreo using a Dev Container, so you can start experimenting without affecting your local environment.

For a deeper understanding of OpenChoreo's architecture, see **[OpenChoreo Concepts](https://openchoreo.dev/docs/category/concepts/)**.

Visit **[Installation Guide](https://openchoreo.dev/docs/getting-started/try-it-out/on-k3d-locally/)** to learn more about installation methods.

## Samples

Explore hands-on examples to help you configure and deploy your applications using OpenChoreo.

- **[Platform Configuration](./samples/platform-config/)** – Set up deployment pipelines and environments.
- **[Deploy from Source](./samples/from-source/)** – Deploy services and web apps from source code.
- **[Deploy from Image](./samples/from-image/)** – Deploy pre-built container images.

Check out the **[Samples Directory](./samples/)** for more details.

## Join the Community & Contribute

We’d love for you to be part of OpenChoreo’s journey! 
Whether you’re fixing a bug, improving documentation, or suggesting new features, every contribution counts.

- **[Contributor Guide](./docs/contributors/README.md)** – Learn how to get started.
- **[Report an Issue](https://github.com/openchoreo/openchoreo/issues)** – Help us improve Choreo.
- **[Join our Slack](https://cloud-native.slack.com/archives/C0ABYRG1MND)** – Be part of the community.

We’re excited to have you onboard!

## Roadmap

We maintain an OpenChoreo Roadmap as a GitHub project board to share what we’re building and when we expect to deliver it.

The roadmap is organized by calendar quarters, and each column represents a set of features or enhancements planned for that period. 
This allows contributors, adopters, and maintainers to understand what’s coming up and what’s already being worked on.

### How It Works

- **Quarterly columns**: Group features by when we aim to deliver them (e.g., 2025 Q2 – Apr–Jun).
- **Future column**: Tracks ideas or initiatives we intend to explore but haven’t scheduled yet.
- Each card links to a GitHub issue with context and discussion.
- We continuously update the roadmap as priorities evolve, and completed features may remain in their quarter for historical visibility.

[OpenChoreo Roadmap](https://github.com/orgs/openchoreo/projects/4/views/2)

## License
OpenChoreo is licensed under Apache 2.0. See the **[LICENSE](./LICENSE)** file for full details.

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fopenchoreo%2Fopenchoreo.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fopenchoreo%2Fopenchoreo?ref=badge_large)




File: .github/pull_request_template.md
---
<!--
PR title must follow Conventional Commits format: type(scope): subject
Scope is optional and subject must start with a lowercase letter.

Examples:
  feat(api): add endpoint for listing components
  fix(controller): handle nil pointer in reconciler
  docs: update contributor guide
  chore(deps): bump sigs.k8s.io/controller-runtime

See: docs/contributors/github_workflow.md#pr-title-convention
-->

## Purpose
> Briefly describe the problem or need driving this PR and how it resolves the issue. Include links to related issues if applicable.

## Approach
> Summarize the solution and implementation details.

## Related Issues
> Include any related issues that are resolved by this PR.

## Checklist
- [ ] Tests added or updated (unit, integration, etc.)
- [ ] Samples updated (if applicable)

## Remarks
> Add any additional context, known issues, or TODOs related to this PR.



File: install/k3d/README.md
---
# k3d Setup for OpenChoreo

Local development setups for OpenChoreo using k3d (k3s in Docker).

## Prerequisites

- Docker 20.10+
- k3d 5.8+
- kubectl 1.32+
- Helm 3.12+

## Setup Options

### Single-Cluster Setup

All OpenChoreo planes run in one k3d cluster.

[See single-cluster/README.md](./single-cluster/README.md)

### Multi-Cluster Setup

Each OpenChoreo plane runs in its own k3d cluster.

[See multi-cluster/README.md](./multi-cluster/README.md)



File: ADOPTERS.md
---
# Adopters
If your organization is using OpenChoreo, we kindly encourage you to add your name to this list.
This helps demonstrate real-world usage, builds community confidence, and strengthens the project’s momentum within the CNCF ecosystem.

Adding your organization is a small contribution that has a big impact. You can do this by opening a pull request to update this file after reviewing our [CONTRIBUTING.md](https://github.com/openchoreo/openchoreo/blob/main/docs/contributors/README.md).

| Organization | Contact | Description |
|--------------|---------|-------------|
| WSO2 | [@manjulaRathnayaka](https://github.com/manjulaRathnayaka) | WSO2 bootstrapped the OpenChoreo project and uses it as the foundational technology behind the WSO2 Cloud platform. OpenChoreo is also used internally as the unified application platform for deploying and operating all internal applications. |





File: install/k3d/multi-cluster/README.md
---
# Multi-Cluster Setup

Production-like setup with each OpenChoreo plane running in its own k3d cluster.

> [!NOTE]
> This guide is for **contributors and developers** working from a local checkout.
> It uses local Helm charts (`install/helm/...`) and standalone setup scripts.
> If you just want to try OpenChoreo, follow the [public getting-started guide](https://openchoreo.dev/docs/getting-started/try-it-out/on-your-environment/) instead.

Planes communicate via **cluster agents** over WebSocket. Data/Build/Observability
plane agents connect to the Control Plane's cluster-gateway. Secured with mTLS,
no need to expose Kubernetes APIs externally.

> [!IMPORTANT]
> Running all 4 clusters requires raising the inotify limit. Without this, k3s nodes
> fail with "too many open files" errors.
> ```bash
> # On Linux (persists until reboot)
> sudo sysctl -w fs.inotify.max_user_instances=1024
> sudo sysctl -w fs.inotify.max_user_watches=524288
>
> # On macOS with Colima/Docker Desktop, run inside the VM:
> docker run --rm --privileged alpine sysctl -w fs.inotify.max_user_instances=1024
> docker run --rm --privileged alpine sysctl -w fs.inotify.max_user_watches=524288
> ```

> [!IMPORTANT]
> If you're using Colima, set `K3D_FIX_DNS=0` when creating clusters.
> See [k3d-io/k3d#1449](https://github.com/k3d-io/k3d/issues/1449).

> [!TIP]
> For faster setup, consider using [Image Preloading](#image-preloading) after creating clusters.

## 1. Control Plane

```bash
k3d cluster create --config install/k3d/multi-cluster/config-cp.yaml
```

### Prerequisites

```bash
# Gateway API CRDs
kubectl apply --context k3d-openchoreo-cp --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/experimental-install.yaml

# cert-manager
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --kube-context k3d-openchoreo-cp \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true

kubectl --context k3d-openchoreo-cp wait --for=condition=Available deployment/cert-manager \
  -n cert-manager --timeout=180s

# kgateway
helm upgrade --install kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --create-namespace --namespace openchoreo-control-plane --kube-context k3d-openchoreo-cp \
  --version v2.2.1

helm upgrade --install kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --namespace openchoreo-control-plane --create-namespace --kube-context k3d-openchoreo-cp \
  --version v2.2.1 \
  --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true
```

### Thunder (Identity Provider)

```bash
helm upgrade --install thunder oci://ghcr.io/asgardeo/helm-charts/thunder \
  --kube-context k3d-openchoreo-cp \
  --namespace thunder \
  --create-namespace \
  --version 0.28.0 \
  --values install/k3d/common/values-thunder.yaml
```

### CoreDNS Rewrite

```bash
kubectl apply --context k3d-openchoreo-cp -f install/k3d/common/coredns-custom.yaml
```

### Backstage Secrets

```bash
kubectl --context k3d-openchoreo-cp create namespace openchoreo-control-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-cp apply -f -

kubectl --context k3d-openchoreo-cp create secret generic backstage-secrets \
  -n openchoreo-control-plane \
  --from-literal=backend-secret="$(head -c 32 /dev/urandom | base64)" \
  --from-literal=client-secret="backstage-portal-secret" \
  --from-literal=jenkins-api-key="placeholder-not-in-use"
```

### Install Control Plane

```bash
helm upgrade --install openchoreo-control-plane install/helm/openchoreo-control-plane \
  --kube-context k3d-openchoreo-cp \
  --namespace openchoreo-control-plane \
  --create-namespace \
  --values install/k3d/multi-cluster/values-cp.yaml
```

```bash
kubectl --context k3d-openchoreo-cp wait -n openchoreo-control-plane \
  --for=condition=available --timeout=300s deployment --all
```

## 2. Install Default Resources

```bash
kubectl --context k3d-openchoreo-cp apply -f samples/getting-started/all.yaml
kubectl --context k3d-openchoreo-cp label namespace default openchoreo.dev/control-plane=true
```

## 3. Data Plane

```bash
k3d cluster create --config install/k3d/multi-cluster/config-dp.yaml

docker exec k3d-openchoreo-dp-server-0 sh -c \
  "cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id"
```

### Prerequisites

```bash
# Gateway API CRDs
kubectl apply --context k3d-openchoreo-dp --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/experimental-install.yaml

# cert-manager
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --kube-context k3d-openchoreo-dp \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true

kubectl --context k3d-openchoreo-dp wait --for=condition=Available deployment/cert-manager \
  -n cert-manager --timeout=180s

# External Secrets Operator
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --kube-context k3d-openchoreo-dp \
  --namespace external-secrets \
  --create-namespace \
  --version 2.0.1 \
  --set installCRDs=true

kubectl --context k3d-openchoreo-dp wait --for=condition=Available deployment/external-secrets \
  -n external-secrets --timeout=180s

# kgateway
helm upgrade --install kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --create-namespace --namespace openchoreo-data-plane --kube-context k3d-openchoreo-dp \
  --version v2.2.1

helm upgrade --install kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --namespace openchoreo-data-plane --create-namespace --kube-context k3d-openchoreo-dp \
  --version v2.2.1 \
  --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true
```

### CoreDNS Rewrite and Certificates

```bash
kubectl apply --context k3d-openchoreo-dp -f install/k3d/common/coredns-custom.yaml

kubectl --context k3d-openchoreo-dp create namespace openchoreo-data-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-dp apply -f -

# Copy cluster-gateway CA from control plane
kubectl --context k3d-openchoreo-cp get secret cluster-gateway-ca \
  -n openchoreo-control-plane \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > /tmp/server-ca.crt

kubectl --context k3d-openchoreo-dp create configmap cluster-gateway-ca \
  --from-file=ca.crt=/tmp/server-ca.crt \
  -n openchoreo-data-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-dp apply -f -
```

### OpenBao (Secret Store)

Install [OpenBao](https://openbao.org/) as the secret backend on the data plane cluster:

```bash
install/prerequisites/openbao/setup.sh --dev --seed-dev-secrets --kube-context k3d-openchoreo-dp
```

This installs OpenBao in dev mode into the `openbao` namespace, configures Kubernetes auth, seeds placeholder development secrets, and creates a `ClusterSecretStore` named `default`.

To use a different secret backend, skip this and create your own `ClusterSecretStore` named `default` following the [ESO provider docs](https://external-secrets.io/latest/provider/).

### Install Data Plane

```bash
helm upgrade --install openchoreo-data-plane install/helm/openchoreo-data-plane \
  --dependency-update \
  --kube-context k3d-openchoreo-dp \
  --namespace openchoreo-data-plane \
  --create-namespace \
  --values install/k3d/multi-cluster/values-dp.yaml
```

```bash
kubectl --context k3d-openchoreo-dp wait -n openchoreo-data-plane \
  --for=condition=available --timeout=300s deployment --all
```

### Register Data Plane

```bash
AGENT_CA=$(kubectl --context k3d-openchoreo-dp get secret cluster-agent-tls \
  -n openchoreo-data-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl --context k3d-openchoreo-cp apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterDataPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  secretStoreRef:
    name: default
  gateway:
    ingress:
      external:
        http:
          host: openchoreoapis.localhost
          listenerName: http
          port: 19080
        name: gateway-default
        namespace: openchoreo-data-plane
EOF
```

## 4. Workflow Plane (Optional)

```bash
k3d cluster create --config install/k3d/multi-cluster/config-wp.yaml

docker exec k3d-openchoreo-wp-server-0 sh -c \
  "cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id"
```

### Prerequisites

```bash
# cert-manager
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --kube-context k3d-openchoreo-wp \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true

kubectl --context k3d-openchoreo-wp wait --for=condition=Available deployment/cert-manager \
  -n cert-manager --timeout=180s

# External Secrets Operator
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --kube-context k3d-openchoreo-wp \
  --namespace external-secrets \
  --create-namespace \
  --version 2.0.1 \
  --set installCRDs=true

kubectl --context k3d-openchoreo-wp wait --for=condition=Available deployment/external-secrets \
  -n external-secrets --timeout=180s
```

### CoreDNS Rewrite and Certificates

```bash
kubectl apply --context k3d-openchoreo-wp -f install/k3d/common/coredns-custom.yaml

kubectl --context k3d-openchoreo-wp create namespace openchoreo-workflow-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-wp apply -f -

# Copy cluster-gateway CA from control plane
kubectl --context k3d-openchoreo-cp get secret cluster-gateway-ca \
  -n openchoreo-control-plane \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > /tmp/server-ca.crt

kubectl --context k3d-openchoreo-wp create configmap cluster-gateway-ca \
  --from-file=ca.crt=/tmp/server-ca.crt \
  -n openchoreo-workflow-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-wp apply -f -
```

### Container Registry

```bash
helm repo add twuni https://twuni.github.io/docker-registry.helm
helm repo update

helm install registry twuni/docker-registry \
  --kube-context k3d-openchoreo-wp \
  --namespace openchoreo-workflow-plane \
  --create-namespace \
  --values install/k3d/multi-cluster/values-registry.yaml
```

### Install Workflow Plane

```bash
helm upgrade --install openchoreo-workflow-plane install/helm/openchoreo-workflow-plane \
  --dependency-update \
  --kube-context k3d-openchoreo-wp \
  --namespace openchoreo-workflow-plane \
  --values install/k3d/multi-cluster/values-wp.yaml
```

### Workflow Templates

The build pipeline is composed of shared ClusterWorkflowTemplates that each handle one step (checkout, build, publish, generate workload). The checkout and publish templates are applied separately so you can replace them to use your own git auth or container registry.

```bash
kubectl --context k3d-openchoreo-wp apply -f samples/getting-started/workflow-templates/checkout-source.yaml
kubectl --context k3d-openchoreo-wp apply -f samples/getting-started/workflow-templates.yaml
kubectl --context k3d-openchoreo-wp apply -f samples/getting-started/workflow-templates/publish-image-k3d.yaml
kubectl --context k3d-openchoreo-wp apply -f samples/getting-started/workflow-templates/generate-workload-k3d.yaml
```

`publish-image-k3d.yaml` pushes images to the local k3d registry at `host.k3d.internal:10082`. To use a different registry, replace this with your own `publish-image` ClusterWorkflowTemplate.

### Buildpack Cache (Optional)

Pre-populates the local registry with buildpack images so Ballerina and Google Cloud Buildpacks workflows don't pull from remote registries on every build. Skip this if you only use Docker or React builds.

```bash
kubectl --context k3d-openchoreo-wp apply -f install/k3d/common/push-buildpack-cache-images.yaml
```

### Register Workflow Plane

```bash
AGENT_CA=$(kubectl --context k3d-openchoreo-wp get secret cluster-agent-tls \
  -n openchoreo-workflow-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl --context k3d-openchoreo-cp apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterWorkflowPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  secretStoreRef:
    name: default
EOF
```

## 5. Observability Plane (Optional)

```bash
k3d cluster create --config install/k3d/multi-cluster/config-op.yaml

docker exec k3d-openchoreo-op-server-0 sh -c \
  "cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id"
```

### Prerequisites

```bash
# Gateway API CRDs
kubectl apply --context k3d-openchoreo-op --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/experimental-install.yaml

# kgateway
helm upgrade --install kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --create-namespace --namespace openchoreo-observability-plane --kube-context k3d-openchoreo-op \
  --version v2.2.1

helm upgrade --install kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --namespace openchoreo-observability-plane --create-namespace --kube-context k3d-openchoreo-op \
  --version v2.2.1 \
  --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true

# cert-manager
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --kube-context k3d-openchoreo-op \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true

kubectl --context k3d-openchoreo-op wait --for=condition=Available deployment/cert-manager \
  -n cert-manager --timeout=180s

# External Secrets Operator
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --kube-context k3d-openchoreo-op \
  --namespace external-secrets \
  --create-namespace \
  --version 2.0.1 \
  --set installCRDs=true

kubectl --context k3d-openchoreo-op wait --for=condition=Available deployment/external-secrets \
  -n external-secrets --timeout=180s

```

### CoreDNS Rewrite and Certificates

```bash
kubectl apply --context k3d-openchoreo-op -f install/k3d/common/coredns-custom.yaml

kubectl --context k3d-openchoreo-op create namespace openchoreo-observability-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-op apply -f -

# Copy cluster-gateway CA from control plane
kubectl --context k3d-openchoreo-cp get secret cluster-gateway-ca \
  -n openchoreo-control-plane \
  -o jsonpath='{.data.ca\.crt}' | base64 -d > /tmp/server-ca.crt

kubectl --context k3d-openchoreo-op create configmap cluster-gateway-ca \
  --from-file=ca.crt=/tmp/server-ca.crt \
  -n openchoreo-observability-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-op apply -f -
```

### OpenBao (Secret Store)

Install [OpenBao](https://openbao.org/) as the secret backend on the observability plane cluster:

```bash
install/prerequisites/openbao/setup.sh --dev --seed-dev-secrets --kube-context k3d-openchoreo-op
```

This installs OpenBao in dev mode into the `openbao` namespace, configures Kubernetes auth, seeds placeholder development secrets, and creates a `ClusterSecretStore` named `default`.

To use a different secret backend, skip this and create your own `ClusterSecretStore` named `default` following the [ESO provider docs](https://external-secrets.io/latest/provider/).

### Observability Plane Secrets

```bash
kubectl --context k3d-openchoreo-op apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: observer-secret
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: observer-secret
  data:
  - secretKey: OPENSEARCH_USERNAME
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: OPENSEARCH_PASSWORD
    remoteRef:
      key: opensearch-password
      property: value
  - secretKey: UID_RESOLVER_OAUTH_CLIENT_SECRET
    remoteRef:
      key: observer-oauth-client-secret
      property: value
EOF

kubectl --context k3d-openchoreo-op wait -n openchoreo-observability-plane \
  --for=condition=Ready externalsecret/observer-secret --timeout=60s
```

### Install Observability Plane

```bash
helm upgrade --install openchoreo-observability-plane install/helm/openchoreo-observability-plane \
  --dependency-update \
  --kube-context k3d-openchoreo-op \
  --namespace openchoreo-observability-plane \
  --create-namespace \
  --values install/k3d/multi-cluster/values-op.yaml
```

```bash
kubectl --context k3d-openchoreo-op wait -n openchoreo-observability-plane \
  --for=condition=available --timeout=600s deployment --all
```

#### Install Observability Modules

Install the logs, metrics, and tracing community modules. The steps below use OpenSearch for logs/tracing and Prometheus for metrics. To use alternative modules visit https://openchoreo.dev/modules.

##### Pre-requisites

Create the `opensearch-admin-credentials` secret needed by the logs and tracing modules:

```bash
kubectl --context k3d-openchoreo-op apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: opensearch-admin-credentials
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: opensearch-admin-credentials
  data:
  - secretKey: username
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: password
    remoteRef:
      key: opensearch-password
      property: value
EOF
```

Create the `openchoreo-observability-plane` namespace and `opensearch-admin-credentials` secret in the data plane cluster:

```bash
kubectl --context k3d-openchoreo-dp create namespace openchoreo-observability-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-dp apply -f -

kubectl --context k3d-openchoreo-dp apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: opensearch-admin-credentials
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: opensearch-admin-credentials
  data:
  - secretKey: username
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: password
    remoteRef:
      key: opensearch-password
      property: value
EOF
```

If the workflow plane is installed, create the namespace and secret there too:

> **Note:** The workflow plane does not have a `ClusterSecretStore`, so the secret is created directly.

```bash
kubectl --context k3d-openchoreo-wp create namespace openchoreo-observability-plane \
  --dry-run=client -o yaml | kubectl --context k3d-openchoreo-wp apply -f -

kubectl --context k3d-openchoreo-wp create secret generic opensearch-admin-credentials \
  -n openchoreo-observability-plane \
  --from-literal=username=admin \
  --from-literal=password=ThisIsTheOpenSearchPassword1
```

##### Logs (observability-logs-opensearch)

Install the OpenSearch operator:

```bash
helm repo add opensearch-operator https://opensearch-project.github.io/opensearch-k8s-operator/
helm repo update
helm upgrade --install opensearch-operator opensearch-operator/opensearch-operator \
  --kube-context k3d-openchoreo-op \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 2.8.0 \
  --set kubeRbacProxy.image.repository=quay.io/brancz/kube-rbac-proxy \
  --set kubeRbacProxy.image.tag=v0.15.0
```

Install the OpenSearch logs module

```bash
helm upgrade --install observability-logs-opensearch \
  oci://ghcr.io/openchoreo/helm-charts/observability-logs-opensearch \
  --kube-context k3d-openchoreo-op \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.3.11 \
  --set openSearchSetup.openSearchSecretName="opensearch-admin-credentials" \
  --set openSearchCluster.credentialsSecretName="opensearch-admin-credentials" \
  --set openSearch.enabled=false \
  --set openSearchCluster.enabled=true
```

Enable Fluent Bit in the data plane cluster:

```bash
helm upgrade --install observability-logs-opensearch \
  oci://ghcr.io/openchoreo/helm-charts/observability-logs-opensearch \
  --kube-context k3d-openchoreo-dp \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.3.11 \
  --set openSearch.enabled=false \
  --set openSearchCluster.enabled=false \
  --set openSearchSetup.enabled=false \
  --set fluent-bit.enabled=true \
  --set fluent-bit.openSearchHost=host.k3d.internal \
  --set fluent-bit.openSearchPort=11085 \
  --set fluent-bit.openSearchVHost=opensearch.observability.openchoreo.localhost
```

If the workflow plane is installed, enable Fluent Bit there too:

```bash
helm upgrade --install observability-logs-opensearch \
  oci://ghcr.io/openchoreo/helm-charts/observability-logs-opensearch \
  --kube-context k3d-openchoreo-wp \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.3.11 \
  --set openSearch.enabled=false \
  --set openSearchCluster.enabled=false \
  --set openSearchSetup.enabled=false \
  --set fluent-bit.enabled=true \
  --set fluent-bit.openSearchHost=host.k3d.internal \
  --set fluent-bit.openSearchPort=11085 \
  --set fluent-bit.openSearchVHost=opensearch.observability.openchoreo.localhost
```

##### Tracing (observability-tracing-opensearch)

Install the tracing receiver in the observability plane cluster. Since the logs module already installed OpenSearch, disable it here:

```bash
helm upgrade --install observability-tracing-opensearch \
  oci://ghcr.io/openchoreo/helm-charts/observability-tracing-opensearch \
  --kube-context k3d-openchoreo-op \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.3.10 \
  --set global.installationMode="multiClusterReceiver" \
  --set openSearch.enabled=false \
  --set openSearchSetup.openSearchSecretName="opensearch-admin-credentials" \
  --set-json opentelemetryCollectorCustomizations.http.hostnames='["opentelemetry.observability.openchoreo.localhost", "host.k3d.internal"]'
```

Install the tracing exporter in the data plane cluster:

```bash
helm upgrade --install observability-tracing-opensearch \
  oci://ghcr.io/openchoreo/helm-charts/observability-tracing-opensearch \
  --kube-context k3d-openchoreo-dp \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.3.10 \
  --set global.installationMode="multiClusterExporter" \
  --set openSearch.enabled=false \
  --set openSearchCluster.enabled=false \
  --set openSearchSetup.enabled=false \
  --set-json opentelemetry-collector.extraEnvs='[]' \
  --set opentelemetryCollectorCustomizations.http.observabilityPlaneUrl="http://host.k3d.internal:11080" \
  --set opentelemetryCollectorCustomizations.http.observabilityPlaneVirtualHost="opentelemetry.observability.openchoreo.localhost"
```

##### Metrics (observability-metrics-prometheus)

```bash
helm upgrade --install observability-metrics-prometheus \
  oci://ghcr.io/openchoreo/helm-charts/observability-metrics-prometheus \
  --kube-context k3d-openchoreo-op \
  --create-namespace \
  --namespace openchoreo-observability-plane \
  --version 0.2.5
```

### Register Observability Plane

```bash
AGENT_CA=$(kubectl --context k3d-openchoreo-op get secret cluster-agent-tls \
  -n openchoreo-observability-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl --context k3d-openchoreo-cp apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterObservabilityPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  observerURL: http://observer.openchoreo.localhost:11080
EOF
```

### Link Other Planes

```bash
kubectl --context k3d-openchoreo-cp patch clusterdataplane default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'

# If cluster workflow plane is installed:
kubectl --context k3d-openchoreo-cp patch clusterworkflowplane default -n default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'
```

## Port Mappings

| Plane               | Cluster           | Kube API | Port Range |
|---------------------|-------------------|----------|------------|
| Control Plane       | k3d-openchoreo-cp | 6550     | 8xxx       |
| Data Plane          | k3d-openchoreo-dp | 6551     | 19xxx      |
| Workflow Plane         | k3d-openchoreo-wp | 6552     | 10xxx      |
| Observability Plane | k3d-openchoreo-op | 6553     | 11xxx      |

All ports are mapped 1:1 (host:container) unless noted.

| Port  | Plane         | Service                |
|-------|---------------|------------------------|
| 8080  | Control       | Gateway HTTP           |
| 8443  | Control       | Gateway HTTPS          |
| 19080 | Data          | Gateway HTTP           |
| 19443 | Data          | Gateway HTTPS          |
| 10081 | Build         | Argo Workflows UI      |
| 10082 | Build         | Container Registry     |
| 11080 | Observability | Observer API (HTTP)    |
| 11081 | Observability | OpenSearch Dashboards* |
| 11082 | Observability | OpenSearch API*        |
| 11084 | Observability | Prometheus*            |
| 11086 | Observability | OpenTelemetry*         |

*Not 1:1 mappings (11081:5601, 11082:9200, 11084:9091, 11086:4317).

## Access Services

| Service              | URL                                           |
|----------------------|-----------------------------------------------|
| OpenChoreo Console   | http://openchoreo.localhost:8080               |
| OpenChoreo API       | http://api.openchoreo.localhost:8080           |
| Thunder Admin        | http://thunder.openchoreo.localhost:8080       |
| Argo Workflows UI    | http://localhost:10081                         |
| Observer API         | http://observer.openchoreo.localhost:11080     |

## Verification

```bash
# All pods
kubectl --context k3d-openchoreo-cp get pods -n openchoreo-control-plane
kubectl --context k3d-openchoreo-dp get pods -n openchoreo-data-plane
kubectl --context k3d-openchoreo-wp get pods -n openchoreo-workflow-plane
kubectl --context k3d-openchoreo-op get pods -n openchoreo-observability-plane

# Plane resources
kubectl --context k3d-openchoreo-cp get clusterdataplane,clusterworkflowplane,clusterobservabilityplane

# Agent connections
kubectl --context k3d-openchoreo-dp logs -n openchoreo-data-plane -l app.kubernetes.io/component=cluster-agent --tail=5
kubectl --context k3d-openchoreo-wp logs -n openchoreo-workflow-plane -l app.kubernetes.io/component=cluster-agent --tail=5
kubectl --context k3d-openchoreo-op logs -n openchoreo-observability-plane -l app.kubernetes.io/component=cluster-agent --tail=5
```

## Image Preloading

Pull images to your host first, then import into each cluster.

```bash
# Control Plane
install/k3d/preload-images.sh \
  --cluster openchoreo-cp \
  --local-charts \
  --control-plane --cp-values install/k3d/multi-cluster/values-cp.yaml \
  --parallel 4

# Data Plane
install/k3d/preload-images.sh \
  --cluster openchoreo-dp \
  --local-charts \
  --data-plane --dp-values install/k3d/multi-cluster/values-dp.yaml \
  --parallel 4

# Workflow Plane
install/k3d/preload-images.sh \
  --cluster openchoreo-wp \
  --local-charts \
  --workflow-plane --wp-values install/k3d/multi-cluster/values-wp.yaml \
  --parallel 4

# Observability Plane
install/k3d/preload-images.sh \
  --cluster openchoreo-op \
  --local-charts \
  --observability-plane --op-values install/k3d/multi-cluster/values-op.yaml \
  --parallel 4
```

Run after creating clusters but before installing anything.

## Cleanup

```bash
k3d cluster delete openchoreo-cp openchoreo-dp openchoreo-wp openchoreo-op
```



File: CODE_OF_CONDUCT.md
---
# Code of Conduct
OpenChoreo adheres to the [CNCF Code of Conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md). All contributors, maintainers, and community members are expected to follow it when participating in project discussions, code contributions, events, and communication channels.



File: SECURITY.md
---
# Security Policy
OpenChoreo takes the security of our users and the ecosystem seriously. We follow industry-standard practices for responsible disclosure and encourage the community to report vulnerabilities safely and privately. 

If you discover a security issue, please do not open a public GitHub issue. Instead, follow the process below.

# Reporting a Vulnerability
To report a security vulnerability, please email: [security@openchoreo.io](mailto:security@openchoreo.io)

Your report should include:
- A description of the issue
- Steps to reproduce (if possible)
- Potential impact
- Any suggested remediation
- Your contact information for follow-up questions


You will receive an acknowledgment within 3 business days.

# Security Response Process
Once a report is received:
1. The security team reviews the issue and determines the severity.
2. A fix is developed privately in a restricted branch or fork.
3. Once validated, the patch is merged and released.
4. Security advisories (GHSA) are published as needed.
5. The reporter is credited unless they request anonymity.

We strive to resolve critical issues as quickly as possible and follow coordinated disclosure best practices.

# Supported Versions
Security fixes will be backported to:
- The latest stable release
- The previous stable minor release (if feasible)


Pre-1.0 releases (0.x) may receive fixes at the discretion of the maintainers.

# Public Communication
Security announcements will be published through:
- GitHub Security Advisories
- Release notes
- The OpenChoreo community channels



File: MAINTAINERS.md
---
# OpenChoreo Maintainers
This file lists the official maintainers of the OpenChoreo project. Maintainers are responsible for the ongoing health of the project, including technical direction, code review, release management, and governance.

All project decisions follow the OpenChoreo Governance Policy and are driven by consensus among maintainers.

## Core Maintainers
Core Maintainers have merge authority across the entire repository and are responsible for stewardship of the project’s long-term roadmap and architectural consistency. Core Maintainers are expected to remain active, participate in design discussions, and provide timely reviews.

In addition to these responsibilities, the Core Maintainers collectively serve as the project’s Security Team, handling security-related issues, coordinating responsible disclosures, and ensuring that patches and advisories are managed appropriately.
- Sameera Jayasoma ([@sameerajayasoma](https://github.com/sameerajayasoma))
- Lakmal Warusawithana ([@lakwarus](https://github.com/lakwarus))
- Binura Gunasekara ([@binura-g](https://github.com/binura-g))
- Tishan Dahanayaka ([@tishan89](https://github.com/tishan89))
- Miraj Abeysekara ([@Mirage20](https://github.com/Mirage20))

## Module / Plane Maintainers
These Maintainers are responsible for specific functional areas of the OpenChoreo codebase. They have merge privileges within their respective domains and participate in cross-project decisions that affect their areas.
- Akila Induranga ([@akila-i](https://github.com/akila-i))
- Binoy Peries ([@binoyPeries](https://github.com/binoyPeries))
- Chalindu Kodikara ([@chalindukodikara](https://github.com/chalindukodikara))
- Chathuranga Dassanayake ([@ChathurangaKCD](https://github.com/ChathurangaKCD))
- Chathurange Siriwardhana ([@chathuranga95](https://github.com/chathuranga95))
- Isala Piyarisi ([@isala404](https://github.com/isala404))
- Janaka Sandaruwan ([@JanakaSandaruwan](https://github.com/JanakaSandaruwan))
- Kavishka Fernando ([@kavishkafernando](https://github.com/kavishkafernando))
- Kavith Lokuhewage ([@kaviththiranga](https://github.com/kaviththiranga))
- Suntharam Ketharan ([@Ketharan](https://github.com/Ketharan))
- Lahiru De Silva ([@NomadXD](https://github.com/NomadXD))
- Lakshan Sivagnanasothy ([@LakshanSS](https://github.com/LakshanSS))
- Mevan Karunanayake ([@mevan-karu](https://github.com/mevan-karu))
- Nilushan Costa ([@nilushancosta](https://github.com/nilushancosta))
- Rashad Sirajudeen ([@rashadism](https://github.com/rashadism))
- Stefinie Fernando ([@stefinie123](https://github.com/stefinie123))
- Vajira Jayasrimal ([@VajiraPrabuddhaka](https://github.com/VajiraPrabuddhaka))
- Yashod Perera ([@yashodgayashan](https://github.com/yashodgayashan))

## Bootstrap Contributors
The following individuals formed the early team that bootstrapped OpenChoreo and contributed to its foundation up to the 0.3 release. Some of these contributors continue to serve as maintainers today, while others have moved on to new areas.

We gratefully acknowledge their role in establishing the project’s core architecture and vision.
- Sameera Jayasoma ([@sameerajayasoma](https://github.com/sameerajayasoma))
- Manjula Rathnayaka ([@manjulaRathnayaka](https://github.com/manjulaRathnayaka))
- Shiro Kulatilake ([@shirolk](https://github.com/shirolk))
- Miraj Abeysekara ([@Mirage20](https://github.com/Mirage20))
- Kavishka Fernando ([@kavishkafernando](https://github.com/kavishkafernando))
- Vajira Jayasrimal ([@VajiraPrabuddhaka](https://github.com/VajiraPrabuddhaka))
- Chalindu Kodikara ([@chalindukodikara](https://github.com/chalindukodikara))
- Jhivan De Benoit ([@jhivandb](https://github.com/jhivandb))




File: samples/component-types/component-http-service/README.md
---
# HTTP Service Component Sample

This sample demonstrates how to deploy an HTTP service component in OpenChoreo with path-based routing.

## Overview

This sample includes the following OpenChoreo Custom Resources:

### ComponentType (`http-service`)

Defines a reusable component type template for HTTP services. It:

- Specifies the workload type as `deployment`
- Defines a schema with configurable parameters (replicas, port, resources)
- Declares environment-specific overrides for resource limits
- Templates the underlying Kubernetes resources (Deployment, Service, HTTPRoute)
- Configures path-based routing with specific HTTP methods:
  - `GET /{component-name}-{endpoint-name}/{resource-paths}`
- Uses CEL expressions to dynamically populate values from component metadata and parameters

This allows you to create multiple HTTP service components using the same template with different configurations.

### Component (`demo-app-http-service`)

Defines the actual HTTP service component using the `http-service` type. It:

- References the `deployment/http-service` component type
- Specifies configuration parameters:
  - 2 replicas
  - Port 8080
  - CPU and memory resource requests/limits
- Belongs to the `default` project

### Workload (`demo-app-http-service-workload`)

Specifies the container image and configuration for the component:

- Links to the `demo-app-http-service` component
- Defines the container image (`ghcr.io/openchoreo/samples/greeter-service:latest`)
- Can specify multiple containers if needed

### ReleaseBinding (`demo-app-development`)

Represents a deployment of the component in a specific environment. It:

- Links to the `demo-app-http-service` component
- Targets the `development` environment
- Refers a ComponentRelease by `releaseName` (This will be overwritten with a generated ComponentRelease as the auto-deploy is enabled) 
- Provides environment-specific overrides (reduced resource limits for dev)

## How It Works

1. **ComponentType** acts as a template/blueprint with path-based routing rules
2. **Component** uses that template and provides base configuration
3. **Workload** specifies what container(s) to run (echo server for testing)
4. **ReleaseBinding** specifies the actual deployment of the component in a specific environment

The OpenChoreo controller manager uses these resources and generates the Kubernetes resources (Deployment, Service, HTTPRoute) based on the templates and parameters.

## Deploy the sample

Apply the sample:

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-http-service/http-service-component.yaml
```

## Check the ReleaseBinding status

```bash
kubectl get releasebinding demo-app-http-service-development -o yaml | grep -A 50 "^status:"
```

## Test the Service by invoking

The service is exposed at the path `/{component-name}-{endpoint-name}`. For this sample, the component name is `demo-app-http-service` and the endpoint name is `http`.

```bash
curl http://development-default.openchoreoapis.localhost:19080/demo-app-http-service-http/greeter/greet
```

Output:
```text
Hello, Stranger!
```

```bash
curl "http://development-default.openchoreoapis.localhost:19080/demo-app-http-service-http/greeter/greet?name=Alice"
```

Output:

```text
Hello, Alice!
```

## Cleanup

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-http-service/http-service-component.yaml
```

## Troubleshooting

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding demo-app-http-service-development -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding demo-app-http-service-development -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=demo-app-http-service -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=demo-app-http-service
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=demo-app-http-service -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=demo-app-http-service --tail=50
   ```

6. **Verify service endpoints:**
   ```bash
   kubectl get service -A -l openchoreo.dev/component=demo-app-http-service
   ```



File: samples/README.md
---
# OpenChoreo Samples

This directory contains sample implementations to help you understand, configure, and use OpenChoreo effectively. These samples demonstrate various deployment patterns and platform capabilities.

## Getting Started Resources

**[Getting Started](./getting-started)** contains the default resources needed to use OpenChoreo. Apply these after installing the control plane:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/getting-started/all.yaml
```

This creates a default project, three environments (development, staging, production), component types (service, web-application, scheduled-task), build workflows, and traits. See the [getting-started README](./getting-started/README.md) for details.

## Sample Categories

### [Deploy from Pre-built Images](./from-image)
Deploy applications using pre-built Docker images. This approach is ideal when you have existing CI systems that build and push container images to registries. These samples show how to deploy your containerized applications directly to OpenChoreo.

**Available Samples:**
- **[Go Greeter Service](./from-image/go-greeter-service/)** - Simple HTTP service demonstrating service deployment
- **[React Starter Web App](./from-image/react-starter-web-app/)** - Web application deployment example
- **[GitHub Issue Reporter](./from-image/issue-reporter-schedule-task/)** - Scheduled task deployment example

### [Build from Source](./from-source)
Build and deploy applications directly from source code using OpenChoreo's built-in CI system. OpenChoreo supports both BuildPacks (for automatic detection and containerization) and Docker (using your Dockerfile) to build applications from source code.

**Services:**
- **[Go Greeter Service (Docker)](./from-source/services/go-docker-greeter/)** - Build from source using Dockerfile
- **[Reading List Service (Buildpack)](./from-source/services/go-google-buildpack-reading-list/)** - Build from source using Google Cloud Buildpacks
- **[Patient Management Service (Buildpack)](./from-source/services/ballerina-buildpack-patient-management/)** - Ballerina service built with Buildpacks

**Web Applications:**
- **[React Starter](./from-source/web-apps/react-starter/)** - React web application built from source

### [Component Types](./component-types)
Low-level examples demonstrating how to define and use custom component types with OpenChoreo's ComponentType CRD. These samples show the underlying mechanics of how components work.

**Available Samples:**
- **[HTTP Service Component](./component-types/component-http-service/)** - Define a reusable HTTP service component type
- **[Web App Component](./component-types/component-web-app/)** - Define a reusable web application component type
- **[Component with Configs](./component-types/component-with-configs/)** - Demonstrate configuration management
- **[Component with Traits](./component-types/component-with-traits/)** - Demonstrate trait composition
- **[Component with Embedded Traits](./component-types/component-with-embedded-traits/)** - Demonstrate PE-defined embedded traits
- **[Component with API Management](./component-types/component-with-api-management/)** - Demonstrate API management via traits

### [Workflows](./workflows)
Reusable Workflow definitions for standalone automation tasks independent of any Component.

**Available Samples:**
- **[AWS RDS Postgres Create](./workflows/aws-rds-postgres-create/)** - Provision and destroy AWS RDS PostgreSQL instances using Terraform
- **[GitHub Stats Report](./workflows/github-stats-report/)** - Fetch GitHub repository statistics, transform the data, and generate a formatted report
- **[SCM Create Repo](./workflows/scm-create-repo/)** - Create repositories in GitHub or AWS CodeCommit

### [GCP Microservices Demo](./gcp-microservices-demo)
A complete microservices application based on Google's popular [microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo). This sample showcases how to deploy a full e-commerce application with multiple interconnected services using OpenChoreo.

### [MCP Server - AI Assistant Integration](./mcp)
Learn how to use OpenChoreo with AI assistants through the Model Context Protocol (MCP). Deploy and manage applications using natural language with AI assistants like Claude Code, Cursor, VS Code, and Claude Desktop.

**Prerequisites:**
- Running OpenChoreo instance
- MCP server configured
- AI assistant installed and configured

**Available Guides:**
- **[Getting Started](./mcp/getting-started/)** - Connect your AI assistant and explore OpenChoreo resources (10-15 min)
- **[Service Deployment](./mcp/service-deployment/)** - Deploy services from source code to production using AI assistants (30-45 min)
  - [Step-by-Step Guide](./mcp/service-deployment/step-by-step/) - Guided walkthrough with explicit prompts
  - [Developer Chat](./mcp/service-deployment/developer-chat/) - Natural conversation-based deployment
- **[Configuration Examples](./mcp/configs/)** - Setup instructions for different AI assistants

### [Platform Configuration](./platform-config)
Configuration samples targeted at Platform Engineers. Learn how to set up deployment pipelines, configure environments, and establish platform governance using OpenChoreo's abstractions.

**Available Configurations:**
- **[Deployment Pipeline](./platform-config/new-deployment-pipeline/)** - Define promotion pipelines across environments
- **[Environments](./platform-config/new-environments/)** - Configure development, QA, pre-production, and production environments



File: samples/component-alerts/README.md
---
## Component Alerts Samples

This sample builds on top of the `gcp-microservices-demo` in `samples/gcp-microservices-demo` and shows how to:

- Attach observability alert rules to existing components as traits
- Configure email and webhook notification channels
- Create controlled failure scenarios to fire those alerts

### Prerequisites

- A running OpenChoreo control plane, data plane, and observability plane
- `kubectl` configured to talk to the cluster where OpenChoreo is installed

### Architecture Overview

This sample uses a simple, role-based workflow:

- **Platform Engineers (one-time setup)**:
  - Deploy the `observability-alert-rule` trait once per OpenChoreo installation
  - Allow the `observability-alert-rule` trait in the desired `ComponentType`. This is already done for you in the default component types `deployment/service` and `deployment/web-application`
  - Configure notification channels once per environment (email, webhook, etc.)

- **Developers (once per component)**:
  - Attach `observability-alert-rule` traits to components
  - The same alert rules are reused as components are promoted across environments

- **Per-environment tuning (by Platform Engineers)**:
  - Use `ReleaseBinding` `traitEnvironmentConfigs` to enable/disable alerts, configure notification channels, toggle incident creation, and toggle AI analysis per environment

### Files in this folder

- `alert-rule-trait.yaml`: The `Trait` definition for `observability-alert-rule` that enables attaching alert rules to components. This trait uses `openAPIV3Schema` format and is typically installed as part of the OpenChoreo control plane, but is included here for reference. **One-time setup by Platform Engineers.**
- `alert-notification-channels.yaml`: Two `ObservabilityAlertsNotificationChannel`s (one email, one webhook) plus their backing `Secret`s for the `development` environment. **One-time setup per environment by Platform Engineers.**
- `components-with-alert-rules.yaml`: `Component` definitions for `frontend`, `recommendation`, and `cart` microservices with alert rules attached as `observability-alert-rule` traits. **Defined once by Developers - alert rules propagate through environments.**
- `failure-scenario-setup.yaml`: `ReleaseBinding`s that deliberately misconfigure the system (env var overrides, CPU / memory limit overrides) to cause alerts to fire. Also demonstrates environment-specific alert customization via `traitEnvironmentConfigs`.
- `trigger-alerts.sh`: Simple script that drives traffic to the `frontend` to trigger the configured alerts.

---

## One-Time Setup (Platform Engineers)

### Step 1: Deploy Alert Rule Trait (One-Time Setup)

Platform Engineers deploy this trait once per OpenChoreo installation so developers can attach alert rules to any component.

The trait is typically installed as part of the OpenChoreo control plane by default unless you have disabled the default resources. If it's not available, you can deploy it manually:

```bash
kubectl apply -f samples/component-alerts/alert-rule-trait.yaml
kubectl get clustertrait observability-alert-rule
```

### Step 2: Configure Notification Channels (One-Time Setup)

Platform Engineers configure notification channels once per environment (email/webhook) and reuse them across all alert rules in that environment.

1. Edit `samples/component-alerts/alert-notification-channels.yaml` and replace the placeholder values:
   - SMTP credentials (host, port, username, password, from/to email addresses)
   - Webhook URL and custom headers (if required)
   - **Email template** (optional): For emails that require specific formatting, you can provide a `template` using CEL expressions. The sample includes a template. If not provided, the raw alertDetails object will be sent.
   - **Webhook payload template** (optional): For webhooks that require specific JSON formats (like Slack), you can provide a `payloadTemplate` using CEL expressions. The sample includes a Slack-compatible template. If not provided, the raw alertDetails object will be sent.

2. Apply the notification channels:
   ```bash
   kubectl apply -f samples/component-alerts/alert-notification-channels.yaml
   ```

3. The notification channels are bounded to the environment. In this sample they are created for the `development` environment. The first notification channel created will be marked as the default notification channel for the environment by OpenChoreo.

---

## Developer Workflow

### Step 3: Deploy the gcp-microservices-demo Sample

Deploy the `gcp-microservices-demo` sample to setup the project and components:
- See `samples/gcp-microservices-demo/README.md` for exact commands.

### Step 4: Define Alert Rules for Components (One-Time per Component)

Developers attach alert rules as traits to components once. These rules automatically propagate to all environments as the component is promoted. Platform Engineers can still customize behavior per environment via `ReleaseBinding` `traitEnvironmentConfigs` (enable/disable, AI analysis, notification channel selection).

This step attaches alert-rule traits to the existing components:

- **Frontend**: Log-based alert that triggers when "rpc error: code = Unavailable" appears more than 5 times within 5 minutes
- **Recommendation**: Metric-based alert that triggers when CPU usage exceeds 80% for 5 minutes
- **Cart**: Metric-based alert that triggers when memory usage exceeds 70% for 2 minutes

Apply the components with alert rules:
```bash
kubectl apply -f samples/component-alerts/components-with-alert-rules.yaml
```

**Note**: The alert rules defined here don't specify notification channels in the trait parameters. Notification channels are configured per environment via `ReleaseBinding` `traitEnvironmentConfigs`. If you want to connect these alert rules to specific notification channels, you can use the `ReleaseBinding` resources in the next section with `traitEnvironmentConfigs` that reference the notification channel names under `actions.notifications.channels` (e.g., `["email-notification-channel-development"]` or `["webhook-notification-channel-development"]`). If not specified, the default notification channel for the environment will be used.

---

## Testing and Verification

### Step 5: Configure Failure Scenarios (Optional - for Testing)

This step creates `ReleaseBinding`s that:
- **Misconfigure resources** to trigger alerts:
  - `frontend`: Override `PRODUCT_CATALOG_SERVICE_ADDR` to `http://localhost:8080` (invalid endpoint) via `workloadOverrides`
  - `recommendation`: Lower CPU limits to `10m` (very restrictive) via `componentTypeEnvironmentConfigs`
  - `cart`: Lower memory requests to `100Mi` and limits to `150Mi` (restrictive) via `componentTypeEnvironmentConfigs`
- **Configure alert rule behavior per environment** via `traitEnvironmentConfigs`:
  - **Frontend alert** (`frontend-rpc-unavailable-error-log-alert`):
    - `enabled: true` - Alert rule is enabled (default is `true`)
    - `actions.notifications.channels: [email-notification-channel-development]` - Uses email notification channel
    - `actions.incident.enabled: true` - Incident creation enabled
    - `actions.incident.triggerAiRca: false` - AI root cause analysis disabled (default is `false`)
  - **Recommendation alert** (`recommendation-high-cpu-alert`):
    - `enabled: true` - Alert rule is enabled
    - `actions.notifications.channels: [webhook-notification-channel-development]` - Uses webhook notification channel
    - `actions.incident.enabled: true` - Incident creation enabled
    - `actions.incident.triggerAiRca: true` - AI root cause analysis enabled
  - **Cart alert** (`cartservice-high-memory-alert`):
    - No `traitEnvironmentConfigs` specified - Uses default values (enabled, no incident creation, no AI analysis, default notification channel for environment)

Apply the failure scenario setup:
```bash
kubectl apply -f samples/component-alerts/failure-scenario-setup.yaml
```

> **Note**: `traitEnvironmentConfigs` let Platform Engineers customize alert rule behavior per environment (enable/disable, notification channels, incident creation, AI analysis) without changing the component definition. If `traitEnvironmentConfigs` are not specified for an alert rule, it uses the defaults (enabled, no incident creation, no AI analysis, default notification channel for the environment). Note that `actions.incident.triggerAiRca: true` requires `actions.incident.enabled: true`; AI RCA can be enabled only when incident creation is explicitly enabled.

### Step 6: Trigger Alerts

Deploy the `trigger-alerts` script to trigger the alerts:
- From the repo root:
  ```bash
  chmod +x samples/component-alerts/trigger-alerts.sh
  ./samples/component-alerts/trigger-alerts.sh
  ```
- This continuously calls the frontend URL to generate load and surface the misconfigurations.

### Step 7: Verify Alerts

Verify the alerts received to configured notification channels:
- For the email channel, check the inbox configured in `alert-notification-channels.yaml`.
- For the webhook channel, check the target endpoint and/or the OpenChoreo observer logs.

---

## Cleanup

Stop the trigger script (Ctrl+C).

Delete the sample resources in reverse order if desired:
```bash
kubectl delete -f samples/component-alerts/failure-scenario-setup.yaml
kubectl delete -f samples/component-alerts/components-with-alert-rules.yaml
kubectl delete -f samples/component-alerts/alert-notification-channels.yaml
# Optionally delete the gcp-microservices-demo resources as well
```

**Note**: If you manually deployed the trait, you can remove it:
```bash
kubectl delete -f samples/component-alerts/alert-rule-trait.yaml
```

---

## Troubleshooting

### Webhook returns 400 Bad Request (e.g., Slack)

**Problem**: Some webhook endpoints (like Slack) require a specific JSON payload format, but OpenChoreo sends the raw alert details object by default.

**Root Cause**:
- OpenChoreo sends by default: `{"ruleName": "...", "description": "...", "severity": "...", ...}`
- Slack expects: `{"text": "...", "blocks": [...]}`

**Solution**: Use the `payloadTemplate` feature in `webhookConfig` to transform the payload format.

**How to use payload templates**:

1. **Add `payloadTemplate` to your webhook configuration**:
   ```yaml
   webhookConfig:
     url: https://hooks.slack.com/services/...
     payloadTemplate: |
       {
         "text": "Alert: ${alertName}",
         "blocks": [
           {
             "type": "section",
             "text": {
               "type": "mrkdwn",
               "text": "*${alertDescription}*\nSeverity: ${alertSeverity}"
             }
           }
         ]
       }
   ```

2. **Available CEL expression variables**:
   - `${alertName}` - Alert rule name
   - `${alertDescription}` - Alert description
   - `${alertSeverity}` - Alert severity (info, warning, critical)
   - `${alertValue}` - Current alert value
   - `${alertThreshold}` - Alert threshold
   - `${alertType}` - Alert type (log, metric)
   - `${component}` - Component name
   - `${project}` - Project name
   - `${environment}` - Environment name
   - `${alertTimestamp}` - Alert timestamp
   - `${componentId}` - Component UID
   - `${projectId}` - Project UID
   - `${environmentId}` - Environment UID
   - `${triggerAiRca}` - Whether AI root cause analysis is enabled for this alert

3. **Example templates**:
   - See `alert-notification-channels.yaml` for a complete Slack template example
   - For other services, customize the JSON structure as needed



File: CHANGELOG.md
---
# Changelog

All notable changes to OpenChoreo are documented in this file.

## v1.0.0

Changes since [v1.0.0-rc.2](https://github.com/openchoreo/openchoreo/releases/tag/v1.0.0-rc.2).

### Features

- **(Backstage UI)** Namespace definition editing with CRUD support via Definition tab for Domain
  entities. ([#479](https://github.com/openchoreo/backstage-plugins/pull/479))

### Enhancements

- **(Backstage UI)** Customized About cards with permission-gated edit links and renamed labels
  (Domain→Namespace, System→Project). ([#479](https://github.com/openchoreo/backstage-plugins/pull/479))
- **(Backstage UI)** Responsive layout for environment cards on wider
  screens. ([#471](https://github.com/openchoreo/backstage-plugins/pull/471))
- **(Backstage UI)** Required field validation in environment variable and file mount
  editors. ([#477](https://github.com/openchoreo/backstage-plugins/pull/477))
- **(Backstage UI)** Pagination for environment cards in deploy
  page. ([#476](https://github.com/openchoreo/backstage-plugins/pull/476))

### Bug Fixes

- **(Controller)** Repeated forbidden errors in controller logs from renderedrelease controller
  Secret listing fixed. ([#2935](https://github.com/openchoreo/openchoreo/pull/2935))
- **(API)** Component release generation missing `spec.workload.dependencies`
  fixed. ([#2934](https://github.com/openchoreo/openchoreo/pull/2934))
- **(MCP)** `create_component` tool parameter description for workflow parameters
  fixed. ([#2925](https://github.com/openchoreo/openchoreo/pull/2925))
- **(CLI)** `occ componentrelease generate` failing for ClusterComponentType and ClusterTrait
  fixed. ([#2928](https://github.com/openchoreo/openchoreo/pull/2928))
- **(Backstage UI)** Promotion path editor allowing same environment as source and target
  fixed. ([#478](https://github.com/openchoreo/backstage-plugins/pull/478))
- **(Backstage UI)** Missing namespace relationship for DeploymentPipeline entities in catalog
  fixed. ([#469](https://github.com/openchoreo/backstage-plugins/pull/469))

## v1.0.0-rc.2

Changes since [v1.0.0-rc.1](https://github.com/openchoreo/openchoreo/releases/tag/v1.0.0-rc.1).

### Breaking Changes

- **(CRD)** `REST` endpoint type removed from Workload. Use `HTTP` instead. ([#2785](https://github.com/openchoreo/openchoreo/pull/2785))
- **(Controller)** NetworkPolicy now allows ingress only from pods with the `openchoreo.dev/system-component` label, tightening data plane project boundary. ([#2876](https://github.com/openchoreo/openchoreo/pull/2876))
- **(Controller)** `connections` renamed to `dependencies` in CEL template context.
  `${connections.*}` becomes `${dependencies.*}` and `toContainerEnv()` becomes
  `toContainerEnvs()`. ([#2912](https://github.com/openchoreo/openchoreo/pull/2912))
- **(CLI)** `occ component scaffold` flags restructured: `--type` renamed to `--componenttype`,
  `--traits` and `--workflow` now resolve namespace-scoped resources only. Use
  `--clustercomponenttype`, `--clustertraits`, and `--clusterworkflow` for cluster-scoped
  resources. ([#2759](https://github.com/openchoreo/openchoreo/pull/2759))

### Features

- **(Controller)** `${workflowplane.secretStore}` context variable in Workflow and ClusterWorkflow
  CEL templates. ([#2902](https://github.com/openchoreo/openchoreo/pull/2902))
- **(MCP)** `query_alerts` and `query_incidents` tools for querying fired alerts and incidents. ([#2751](https://github.com/openchoreo/openchoreo/pull/2751))
- **(MCP)** `create_release_binding` tool for deploying a component release to an environment. ([#2794](https://github.com/openchoreo/openchoreo/pull/2794))
- **(Backstage UI)** Resource definition tab for Component and Project entities. ([#423](https://github.com/openchoreo/backstage-plugins/pull/423), [#453](https://github.com/openchoreo/backstage-plugins/pull/453))
- **(Backstage UI)** Template quick-create from search with type-specific icons. ([#454](https://github.com/openchoreo/backstage-plugins/pull/454))

### Enhancements

- **(CRD)** Admission webhook validation for Workflow and ClusterWorkflow resources. ([#2847](https://github.com/openchoreo/openchoreo/pull/2847))
- **(CRD)** OpenAPI v3 JSON Schema validation for ComponentType, ClusterComponentType, Trait, and ClusterTrait schema fields. ([#2852](https://github.com/openchoreo/openchoreo/pull/2852))
- **(CRD)** Validation rejects resource templates with hardcoded `metadata.namespace`; only `${metadata.namespace}` allowed. ([#2832](https://github.com/openchoreo/openchoreo/pull/2832))
- **(CRD)** Typed return types for CEL helper functions, enabling validation of field access errors in `forEach` loops. ([#2850](https://github.com/openchoreo/openchoreo/pull/2850))
- **(CRD)** Improved workload generation workflow template. ([#2819](https://github.com/openchoreo/openchoreo/pull/2819))
- **(API)** `deletionTimestamp` and `deletionGracePeriodSeconds` fields added to ObjectMeta schema. ([#2853](https://github.com/openchoreo/openchoreo/pull/2853))
- **(MCP)** Component dependencies exposed in `get_component_release` and `get_release_binding` tools. ([#2835](https://github.com/openchoreo/openchoreo/pull/2835))
- **(MCP)** Platform engineer toolset enabled by default. ([#2747](https://github.com/openchoreo/openchoreo/pull/2747))
- **(CLI)** Mixed-scope resources in `occ component scaffold` with `--clustercomponenttype`, `--clustertraits`, and `--clusterworkflow` flags. ([#2759](https://github.com/openchoreo/openchoreo/pull/2759))
- **(CLI)** Short flags `-n` (namespace), `-p` (project), `-c` (component) for common options. ([#2833](https://github.com/openchoreo/openchoreo/pull/2833))
- **(Helm)** Backstage authentication `redirectFlow` toggle for login mode. ([#2834](https://github.com/openchoreo/openchoreo/pull/2834))
- **(Helm)** Removed OpenTelemetry Collector, Fluent Bit, and unused observability plane sub-chart dependencies from Helm charts. ([#2878](https://github.com/openchoreo/openchoreo/pull/2878), [#2809](https://github.com/openchoreo/openchoreo/pull/2809), [#2737](https://github.com/openchoreo/openchoreo/pull/2737))
- **(Helm)** Thunder bumped to v0.28.0 with improved user attribute handling. ([#2776](https://github.com/openchoreo/openchoreo/pull/2776))
- **(Backstage UI)** Deployment pipeline selector in project creation and project overview page. ([#419](https://github.com/openchoreo/backstage-plugins/pull/419), [#420](https://github.com/openchoreo/backstage-plugins/pull/420))
- **(Backstage UI)** Endpoint editor improvements: schema type auto-derived from endpoint type, schema-aware placeholders, and API entities created only for endpoints with schemas. ([#428](https://github.com/openchoreo/backstage-plugins/pull/428))
- **(Backstage UI)** Entity ownership resolution from `backstage.io/owner` CR annotations. ([#434](https://github.com/openchoreo/backstage-plugins/pull/434))
- **(Backstage UI)** Workload details (container images, repository, revision) in workflow run details view. ([#436](https://github.com/openchoreo/backstage-plugins/pull/436))
- **(Backstage UI)** Deletion-marked visual indicators on catalog graph nodes. ([#437](https://github.com/openchoreo/backstage-plugins/pull/437))
- **(Backstage UI)** Workflow run retention time (TTL) display. ([#445](https://github.com/openchoreo/backstage-plugins/pull/445))
- **(Backstage UI)** Edit functionality in role binding detail dialog. ([#447](https://github.com/openchoreo/backstage-plugins/pull/447))
- **(Backstage UI)** Overhauled search with Cmd+K/Ctrl+K shortcut, kind icons, and custom filters. ([#448](https://github.com/openchoreo/backstage-plugins/pull/448))
- **(Backstage UI)** Custom recently visited card with kind-aware colors and icons. ([#449](https://github.com/openchoreo/backstage-plugins/pull/449))
- **(Backstage UI)** "Cluster" role type chip in namespace role binding views. ([#421](https://github.com/openchoreo/backstage-plugins/pull/421))
- **(Backstage UI)** Improved array field display and description styling in scaffolder forms. ([#418](https://github.com/openchoreo/backstage-plugins/pull/418))
- **(Backstage UI)** Scaffolder review step rewritten with template-aware structured sections. ([#426](https://github.com/openchoreo/backstage-plugins/pull/426))
- **(Backstage UI)** Default role templates updated with platformEngineer and SRE roles. ([#425](https://github.com/openchoreo/backstage-plugins/pull/425))
- **(Backstage UI)** Default log sort order changed to ascending (oldest first). ([#442](https://github.com/openchoreo/backstage-plugins/pull/442))
- **(Backstage UI)** Log entry copy button always visible instead of hover-only. ([#446](https://github.com/openchoreo/backstage-plugins/pull/446))
- **(Backstage UI)** Sign-in flow switched from popup to redirect-based OAuth by default. ([#440](https://github.com/openchoreo/backstage-plugins/pull/440))
- **(Backstage UI)** Separate view permissions for alerts and incidents. ([#462](https://github.com/openchoreo/backstage-plugins/pull/462))
- **(Backstage UI)** Git secrets management UI improved with search, redesigned toolbar, and improved dialog layouts. ([#465](https://github.com/openchoreo/backstage-plugins/pull/465))
- **(Backstage UI)** "Invoke URLs" renamed to "Endpoint URLs" with clickable links. ([#467](https://github.com/openchoreo/backstage-plugins/pull/467))
- **(Backstage UI)** Default or first namespace pre-selected during resource creation. ([#457](https://github.com/openchoreo/backstage-plugins/pull/457))
- **(Backstage UI)** Helper texts for environment variables and file mounts in Workload Editor. ([#455](https://github.com/openchoreo/backstage-plugins/pull/455))
- **(Backstage UI)** Keyboard shortcut hint shown in search modal with improved auto-focus. ([#451](https://github.com/openchoreo/backstage-plugins/pull/451))
- **(Backstage UI)** "promotesTo/promotedBy" relationship labels renamed to "deploysTo/deployedBy". ([#456](https://github.com/openchoreo/backstage-plugins/pull/456))
- **(Backstage UI)** "OpenChoreo Catalog" page title renamed to "Catalog". ([#459](https://github.com/openchoreo/backstage-plugins/pull/459))
- **(Backstage UI)** Deletion badge and disabled navigation for entities marked for deletion. ([#463](https://github.com/openchoreo/backstage-plugins/pull/463))

### Bug Fixes

- **(Controller)** Environment finalizer stuck in infinite retry when deleting namespace with ClusterDataPlane reference fixed. ([#2769](https://github.com/openchoreo/openchoreo/pull/2769))
- **(Controller)** ReleaseBindings not deleted during environment deletion fixed. ([#2881](https://github.com/openchoreo/openchoreo/pull/2881))
- **(Controller)** DataPlane and ClusterDataPlane status not persisted when cluster-gateway unreachable fixed. ([#2778](https://github.com/openchoreo/openchoreo/pull/2778))
- **(Controller)** Trait schema cache collisions when Trait and ClusterTrait share the same name fixed. ([#2842](https://github.com/openchoreo/openchoreo/pull/2842))
- **(Controller)** Workflow run deletion failing for ClusterWorkflow references fixed. ([#2875](https://github.com/openchoreo/openchoreo/pull/2875))
- **(Controller)** Intermittent agent disconnects when HA (multiple replicas) enabled fixed. ([#2828](https://github.com/openchoreo/openchoreo/pull/2828))
- **(Controller)** Default component type descriptions corrected. ([#2732](https://github.com/openchoreo/openchoreo/pull/2732))
- **(CLI)** Server error messages now shown instead of bare HTTP status codes. ([#2738](https://github.com/openchoreo/openchoreo/pull/2738))
- **(CLI)** Descriptive error shown for missing positional arguments instead of generic message. ([#2780](https://github.com/openchoreo/openchoreo/pull/2780))
- **(Helm)** Missing default role permissions for component CRUD, secret references, and observability management fixed. ([#2761](https://github.com/openchoreo/openchoreo/pull/2761))
- **(Helm)** Missing Helm values for quick-start observability MCP server fixed. ([#2745](https://github.com/openchoreo/openchoreo/pull/2745))
- **(Helm)** Missing `workload:view` permission in workload-publisher role fixed. ([#2904](https://github.com/openchoreo/openchoreo/pull/2904))
- **(Observability)** Observer API `total` field in logs, traces, and spans responses returning item count instead of total result count fixed. ([#2911](https://github.com/openchoreo/openchoreo/pull/2911))
- **(Install)** `check-status.sh` script updated to use correct component labels and namespaces. ([#2820](https://github.com/openchoreo/openchoreo/pull/2820))
- **(Backstage UI)** Deny policies ignored in permission evaluation and catalog visibility fixed. ([#439](https://github.com/openchoreo/backstage-plugins/pull/439))
- **(Backstage UI)** Role deletion with active bindings now prevented with clear error. ([#424](https://github.com/openchoreo/backstage-plugins/pull/424))
- **(Backstage UI)** Display names not appearing consistently in breadcrumb navigation fixed. ([#438](https://github.com/openchoreo/backstage-plugins/pull/438))
- **(Backstage UI)** Endpoints tab incorrectly showing for CronJob/Job types fixed. ([#443](https://github.com/openchoreo/backstage-plugins/pull/443))
- **(Backstage UI)** Environment overrides using latest workload instead of component release snapshot fixed. ([#430](https://github.com/openchoreo/backstage-plugins/pull/430))
- **(Backstage UI)** Traces waterfall view span color fixed. ([#468](https://github.com/openchoreo/backstage-plugins/pull/468))
- **(Backstage UI)** Cluster workflow creation failing with template fixed. ([#460](https://github.com/openchoreo/backstage-plugins/pull/460))
- **(Backstage UI)** Microsoft Entra JWT claims for profile extraction during sign-in fixed. ([#458](https://github.com/openchoreo/backstage-plugins/pull/458))
- **(Backstage UI)** Row height overflow and horizontal scroll in project components card fixed. ([#452](https://github.com/openchoreo/backstage-plugins/pull/452))

## v1.0.0-rc.1

Changes since [v0.17.0](https://github.com/openchoreo/openchoreo/releases/tag/v0.17.0).

### Breaking Changes

- **(CRD)** BuildPlane renamed to WorkflowPlane. `BuildPlane` → `WorkflowPlane`,
  `ClusterBuildPlane` → `ClusterWorkflowPlane`. ([#2574](https://github.com/openchoreo/openchoreo/pull/2574))
- **(CRD)** Schema definition changed to openAPIV3Schema. ComponentTypes, Traits, and Workflows now
  use standard OpenAPI v3 schema format. The old inline schema syntax is no longer
  supported. ([#2547](https://github.com/openchoreo/openchoreo/pull/2547), [#2539](https://github.com/openchoreo/openchoreo/pull/2539), [#2679](https://github.com/openchoreo/openchoreo/pull/2679))
  ```yaml
  # Before
  schema:
    parameters:
      replicas: "integer | default=1"

  # After
  parameters:
    openAPIV3Schema:
      type: object
      properties:
        replicas:
          type: integer
          default: 1
  ```
- **(CRD)** Connections renamed to Dependencies in Workload. The `connections` field is now
  `dependencies` with a restructured spec. ([#2510](https://github.com/openchoreo/openchoreo/pull/2510), [#2531](https://github.com/openchoreo/openchoreo/pull/2531))
- **(CRD)** `AuthzClusterRole` renamed to `ClusterAuthzRole`. CRD names follow Kubernetes naming
  conventions with `Cluster` prefix. ([#2606](https://github.com/openchoreo/openchoreo/pull/2606))
  ```yaml
  # Before
  kind: AuthzClusterRole
  # After
  kind: ClusterAuthzRole
  ```
- **(CRD)** `AuthzClusterRoleBinding` renamed to `ClusterAuthzRoleBinding`. ([#2606](https://github.com/openchoreo/openchoreo/pull/2606))
  ```yaml
  # Before
  kind: AuthzClusterRoleBinding
  # After
  kind: ClusterAuthzRoleBinding
  ```
- **(CRD)** `secretRef` renamed to `secretKeyRef` across CRDs. Affects DataPlane, ClusterDataPlane,
  and Workload resources. ([#2642](https://github.com/openchoreo/openchoreo/pull/2642))
- **(CRD)** `traitOverrides` renamed to `traitEnvironmentConfigs` in ReleaseBinding. Also
  `componentTypeEnvOverrides` → `componentTypeEnvironmentConfigs`. ([#2607](https://github.com/openchoreo/openchoreo/pull/2607))
- **(CRD)** `targetPath` renamed to `scope` in AuthzRoleBinding. ([#2580](https://github.com/openchoreo/openchoreo/pull/2580))
- **(CRD)** Role binding specs support multiple role mappings. Single `roleRef` + `targetPath`
  replaced with `roleMappings` array in both `AuthzRoleBinding` and
  `ClusterAuthzRoleBinding`. ([#2568](https://github.com/openchoreo/openchoreo/pull/2568))
  ```yaml
  # Before
  spec:
    roleRef:
      kind: AuthzRole
      name: developer
    targetPath:
      project: my-project

  # After
  spec:
    roleMappings:
      - roleRef:
          kind: AuthzRole
          name: developer
        scope:
          project: my-project
  ```
- **(CRD)** Removed approval fields from DeploymentPipeline. `requiresApproval` and
  `isManualApprovalRequired` removed from `spec.promotionPaths[].targetEnvironmentRefs[]`.
  `sourceEnvironmentRef` changed from string to object with `kind` and `name`
  fields. ([#2651](https://github.com/openchoreo/openchoreo/pull/2651))
- **(CRD)** DeploymentPipelineRef changed from string to object. Now requires `kind` and `name`
  fields. ([#2461](https://github.com/openchoreo/openchoreo/pull/2461))
  ```yaml
  # Before
  deploymentPipelineRef: my-pipeline

  # After
  deploymentPipelineRef:
    kind: DeploymentPipeline
    name: my-pipeline
  ```
- **(CRD)** DeploymentPipeline environment references changed to objects. `kind` field added to
  `spec.promotionPaths[].targetEnvironmentRefs[]`. `spec.promotionPaths[].sourceEnvironmentRef`
  changed from string to object with `kind` and `name`
  fields. ([#2544](https://github.com/openchoreo/openchoreo/pull/2544), [#2594](https://github.com/openchoreo/openchoreo/pull/2594))
- **(CRD)** ComponentRelease traits changed from map to array. Traits now include `kind`, `name`,
  and `spec` fields. ComponentType reference also includes `kind` and `name`. ([#2694](https://github.com/openchoreo/openchoreo/pull/2694), [#2687](https://github.com/openchoreo/openchoreo/pull/2687))
- **(CRD)** Default workflow ref kind changed to ClusterWorkflow. Component and WorkflowRun workflow
  references now default to `ClusterWorkflow` kind instead of `Workflow`. ([#2667](https://github.com/openchoreo/openchoreo/pull/2667))
- **(CRD)** ObservabilityAlertRule restructured. Removed `enableAiRootCauseAnalysis` and
  `notificationChannel` fields. Replaced with `actions` struct containing `notifications` and
  optional `incident` configuration. ([#2470](https://github.com/openchoreo/openchoreo/pull/2470))
- **(CRD)** `imagePullSecretRefs` removed from DataPlane and ClusterDataPlane. ([#2297](https://github.com/openchoreo/openchoreo/pull/2297))
- **(CRD)** `openchoreo.dev/controlplane-namespace` label renamed to
  `openchoreo.dev/control-plane`. ([#2576](https://github.com/openchoreo/openchoreo/pull/2576), [#2668](https://github.com/openchoreo/openchoreo/pull/2668), [#2681](https://github.com/openchoreo/openchoreo/pull/2681))
- **(CRD)** Workflow authz role renamed to `workload-publisher`. ([#2497](https://github.com/openchoreo/openchoreo/pull/2497))
- **(CRD)** Deprecated CRDs removed: ConfigurationGroup, Build, GitCommitRequest,
  DeploymentTrack. ([#2297](https://github.com/openchoreo/openchoreo/pull/2297))
- **(CRD)** Release CRD renamed to RenderedRelease. All references to `Release` resources must be
  updated to `RenderedRelease`. ([#2484](https://github.com/openchoreo/openchoreo/pull/2484))
- **(CRD)** `suspend` state removed from ReleaseBinding. ([#2706](https://github.com/openchoreo/openchoreo/pull/2706))
- **(CRD)** Workflow ref is now immutable in WorkflowRun. Workflow kind and name cannot be changed
  after creation. ([#2657](https://github.com/openchoreo/openchoreo/pull/2657))
- **(CRD)** `api-configuration` trait removed from default resources. ([#2684](https://github.com/openchoreo/openchoreo/pull/2684))
- **(API)** Legacy API routes removed. The `/legacy` prefix fallback and migration router have been
  removed. All clients must use the current API routes. ([#2588](https://github.com/openchoreo/openchoreo/pull/2588))
- **(API)** Deploy and promote endpoints removed. Use ReleaseBinding CRUD operations
  instead. ([#2569](https://github.com/openchoreo/openchoreo/pull/2569))
- **(API)** Legacy release resource endpoints removed. ([#2551](https://github.com/openchoreo/openchoreo/pull/2551))
- **(API)** ListActions API returns `ActionInfo` objects. Previously returned plain string arrays,
  now returns objects with `name` and `lowestScope` fields. ([#2602](https://github.com/openchoreo/openchoreo/pull/2602))
- **(API)** `releases` renamed to `renderedReleases` in resource tree API response. ([#2500](https://github.com/openchoreo/openchoreo/pull/2500))
- **(API)** Observer URL and RCA agent URL endpoints removed. ([#2466](https://github.com/openchoreo/openchoreo/pull/2466))
- **(API)** User types endpoint path updated to include authentication prefix. ([#2524](https://github.com/openchoreo/openchoreo/pull/2524))
- **(API)** `user_types` renamed to `subject_types` in observer auth config. ([#2534](https://github.com/openchoreo/openchoreo/pull/2534))
- **(API)** Legacy auto-build HTTP handler removed. ([#2518](https://github.com/openchoreo/openchoreo/pull/2518))
- **(API)** `component:deploy` permission action removed from action registry. ([#2597](https://github.com/openchoreo/openchoreo/pull/2597))
- **(CLI)** `--set` flag uses Helm-style paths. Override paths now follow Helm
  conventions. ([#2537](https://github.com/openchoreo/openchoreo/pull/2537))
- **(Helm)** Build plane chart renamed to `openchoreo-workflow-plane`. The `openchoreo-build-plane`
  chart no longer exists. ([#2574](https://github.com/openchoreo/openchoreo/pull/2574))
- **(Helm)** WSO2 API platform chart removed from data plane Helm chart. Now available as a
  community module. ([#2646](https://github.com/openchoreo/openchoreo/pull/2646))
- **(Helm)** Default observability module charts removed from observability-plane Helm chart. Now
  available as community modules. ([#2675](https://github.com/openchoreo/openchoreo/pull/2675))
- **(Helm)** Observer role renamed to `observer-resource-reader`. ([#2661](https://github.com/openchoreo/openchoreo/pull/2661))
- **(Backstage UI)** Build plane renamed to workflow plane throughout the UI. ([#375](https://github.com/openchoreo/backstage-plugins/pull/375))

### Features

- **(CRD)** ClusterWorkflow resource added. Cluster-scoped version of Workflow for shared workflow definitions. ([#2465](https://github.com/openchoreo/openchoreo/pull/2465))
- **(CRD)** Cluster-scoped resources (ClusterComponentType, ClusterTrait, ClusterWorkflow) used as default platform resources. ([#2532](https://github.com/openchoreo/openchoreo/pull/2532))
- **(CRD)** Cluster trait validation support. ([#2486](https://github.com/openchoreo/openchoreo/pull/2486))
- **(CRD)** Scope field in ClusterAuthzRoleBinding for scoped access control. ([#2591](https://github.com/openchoreo/openchoreo/pull/2591))
- **(CRD)** Component workflow validation in WorkflowRun. ([#2667](https://github.com/openchoreo/openchoreo/pull/2667))
- **(API)** ComponentRelease create and delete endpoints. ([#2620](https://github.com/openchoreo/openchoreo/pull/2620))
- **(API)** `labelSelector` query parameter for all list APIs. ([#2560](https://github.com/openchoreo/openchoreo/pull/2560))
- **(API)** `apiVersion` and `kind` fields in all CRD API responses. ([#2456](https://github.com/openchoreo/openchoreo/pull/2456))
- **(API)** Alerts, incidents querying and incident update endpoints. ([#2527](https://github.com/openchoreo/openchoreo/pull/2527), [#2550](https://github.com/openchoreo/openchoreo/pull/2550))
- **(API)** Alert and incident entry storage for observability plane. ([#2509](https://github.com/openchoreo/openchoreo/pull/2509))
- **(API)** CRUD endpoints for cluster workflows. ([#2489](https://github.com/openchoreo/openchoreo/pull/2489))
- **(API)** Git secret creation with cluster workflow plane support. ([#2700](https://github.com/openchoreo/openchoreo/pull/2700))
- **(CLI)** ClusterWorkflow commands: apply, list, get, delete, run, logs. ([#2494](https://github.com/openchoreo/openchoreo/pull/2494), [#2653](https://github.com/openchoreo/openchoreo/pull/2653), [#2674](https://github.com/openchoreo/openchoreo/pull/2674))
- **(CLI)** ClusterWorkflowPlane list, get, and delete commands. ([#2691](https://github.com/openchoreo/openchoreo/pull/2691))
- **(CLI)** ClusterDataPlane and ClusterObservabilityPlane commands. ([#2680](https://github.com/openchoreo/openchoreo/pull/2680))
- **(CLI)** Workflow delete command. ([#2601](https://github.com/openchoreo/openchoreo/pull/2601))
- **(CLI)** `--tail` flag for `component logs` command. ([#2533](https://github.com/openchoreo/openchoreo/pull/2533))
- **(Helm)** Default authorization roles (admin, developer, sre, platform-engineer) shipped in Helm values. ([#2268](https://github.com/openchoreo/openchoreo/pull/2268))
- **(MCP)** Manage cluster workflows. ([#2489](https://github.com/openchoreo/openchoreo/pull/2489))
- **(MCP)** Platform engineering tools for managing ComponentTypes, Traits, ComponentReleases, DeploymentPipelines, and cluster plane resources. ([#2599](https://github.com/openchoreo/openchoreo/pull/2599))
- **(Observability)** Configurable JWT auth for RCA agent and refined remediation model. ([#2614](https://github.com/openchoreo/openchoreo/pull/2614))
- **(Samples)** AWS RDS PostgreSQL create/delete generic workflow sample. ([#2577](https://github.com/openchoreo/openchoreo/pull/2577))
- **(Backstage UI)** Alerts and incidents support in observability plugin with incident indicators on environment cards. ([#361](https://github.com/openchoreo/backstage-plugins/pull/361), [#344](https://github.com/openchoreo/backstage-plugins/pull/344), [#371](https://github.com/openchoreo/backstage-plugins/pull/371))
- **(Backstage UI)** Cluster-scoped resource support: ClusterWorkflow page, ClusterDataPlane entities, and dynamic kind filtering. ([#364](https://github.com/openchoreo/backstage-plugins/pull/364), [#382](https://github.com/openchoreo/backstage-plugins/pull/382), [#370](https://github.com/openchoreo/backstage-plugins/pull/370), [#345](https://github.com/openchoreo/backstage-plugins/pull/345))
- **(Backstage UI)** Permission-based access control: proactive permission checks, permission filtering, 403 error handling, and permission gates for traces and RCA. ([#359](https://github.com/openchoreo/backstage-plugins/pull/359), [#358](https://github.com/openchoreo/backstage-plugins/pull/358), [#351](https://github.com/openchoreo/backstage-plugins/pull/351), [#356](https://github.com/openchoreo/backstage-plugins/pull/356), [#363](https://github.com/openchoreo/backstage-plugins/pull/363), [#366](https://github.com/openchoreo/backstage-plugins/pull/366), [#386](https://github.com/openchoreo/backstage-plugins/pull/386))
- **(Backstage UI)** Access control views updated with cluster role and mapping permissions support. ([#380](https://github.com/openchoreo/backstage-plugins/pull/380), [#378](https://github.com/openchoreo/backstage-plugins/pull/378), [#385](https://github.com/openchoreo/backstage-plugins/pull/385))
- **(Backstage UI)** Delete support for all OpenChoreo resource types. ([#377](https://github.com/openchoreo/backstage-plugins/pull/377))
- **(Backstage UI)** DeploymentPipeline scaffolder template with permission checks. ([#383](https://github.com/openchoreo/backstage-plugins/pull/383))
- **(Backstage UI)** Component trait configs moved to deploy page with revamped configure and deploy wizard. ([#362](https://github.com/openchoreo/backstage-plugins/pull/362))
- **(Backstage UI)** Hierarchy-aware navigation breadcrumbs. ([#367](https://github.com/openchoreo/backstage-plugins/pull/367))
- **(Backstage UI)** Context-aware create button on catalog page. ([#393](https://github.com/openchoreo/backstage-plugins/pull/393))
- **(Backstage UI)** Form/YAML toggle for workflow trigger with custom build parameters support. ([#350](https://github.com/openchoreo/backstage-plugins/pull/350), [#399](https://github.com/openchoreo/backstage-plugins/pull/399))
- **(Backstage UI)** `displayName` field added to YAML editors and templates in scaffolder. ([#400](https://github.com/openchoreo/backstage-plugins/pull/400))
- **(Backstage UI)** Skeleton loaders added to create page during template loading. ([#405](https://github.com/openchoreo/backstage-plugins/pull/405))
- **(Backstage UI)** DeploymentStatusCard replacing ProductionOverviewCard. ([#395](https://github.com/openchoreo/backstage-plugins/pull/395))
- **(Backstage UI)** Deselect-all toggle for kind and project filters. ([#372](https://github.com/openchoreo/backstage-plugins/pull/372))
- **(Backstage UI)** Catalog listing external icon opens in new tab. ([#391](https://github.com/openchoreo/backstage-plugins/pull/391))
- **(Backstage UI)** Workflow plane linked to workflow with project mapping removed. ([#389](https://github.com/openchoreo/backstage-plugins/pull/389))
- **(Backstage UI)** ObservabilityProjectRuntimeLogs component. ([#335](https://github.com/openchoreo/backstage-plugins/pull/335))
- **(Backstage UI)** EntityRelationWarning made collapsible with platform kinds filtered. ([#360](https://github.com/openchoreo/backstage-plugins/pull/360))
- **(Backstage UI)** Auth providers section removed from settings. ([#342](https://github.com/openchoreo/backstage-plugins/pull/342))
- **(Backstage UI)** WorkflowRun management support for cluster-scoped workflows, including view, trigger, and logs. ([#392](https://github.com/openchoreo/backstage-plugins/pull/392), [#376](https://github.com/openchoreo/backstage-plugins/pull/376))

### Enhancements

- **(CRD)** Workflow annotations replaced with labels and schema extensions. ([#2616](https://github.com/openchoreo/openchoreo/pull/2616))
- **(CRD)** Paketo buildpack builder introduced for build workflows. ([#2557](https://github.com/openchoreo/openchoreo/pull/2557))
- **(CLI)** Command aliases improved for consistency. ([#2565](https://github.com/openchoreo/openchoreo/pull/2565))
- **(CLI)** `--set` value typing and escaped-dot handling hardened. ([#2541](https://github.com/openchoreo/openchoreo/pull/2541))
- **(CLI)** Command descriptions updated for cluster authz role and binding commands. ([#2615](https://github.com/openchoreo/openchoreo/pull/2615))
- **(Helm)** External secret references used in observability plane. ([#2554](https://github.com/openchoreo/openchoreo/pull/2554))
- **(Helm)** Thunder v0.24.0 → v0.26.0 ([#2593](https://github.com/openchoreo/openchoreo/pull/2593))
- **(Observability)** RCA agent report backend switched from OpenSearch to SQLite (default) with PostgreSQL support. ([#2468](https://github.com/openchoreo/openchoreo/pull/2468))
- **(Backstage UI)** RCA quick fixes refactored to singular change field and file card UI. ([#374](https://github.com/openchoreo/backstage-plugins/pull/374))
- **(Backstage UI)** Environment overview cards (hosted environments, linked planes, pipelines, deployed components) made clickable with consistent styling. ([#390](https://github.com/openchoreo/backstage-plugins/pull/390))
- **(Backstage UI)** Cell diagram and platform graph panning, zoom, and positioning improved. ([#336](https://github.com/openchoreo/backstage-plugins/pull/336), [#337](https://github.com/openchoreo/backstage-plugins/pull/337))
- **(Backstage UI)** Scaffolder review step shows full path for selected scope. ([#334](https://github.com/openchoreo/backstage-plugins/pull/334))
- **(Backstage UI)** API page cards reordered with duplicate namespace filter removed. ([#388](https://github.com/openchoreo/backstage-plugins/pull/388))
- **(Backstage UI)** Component creation steps reordered. ([#410](https://github.com/openchoreo/backstage-plugins/pull/410))
- **(Backstage UI)** More resource YAML fields (uid, creationTimestamp, generation, status) shown in Definition Tab editor. ([#408](https://github.com/openchoreo/backstage-plugins/pull/408))
- **(Backstage UI)** Git secret creation scoped to workflow plane with improved secret filtering. ([#406](https://github.com/openchoreo/backstage-plugins/pull/406))

### Bug Fixes

- **(CRD)** Missing types in workflow schemas fixed. ([#2521](https://github.com/openchoreo/openchoreo/pull/2521))
- **(API)** Component validation removed from update path. ([#2631](https://github.com/openchoreo/openchoreo/pull/2631))
- **(API)** Generate release endpoint fixed to handle embedded traits. ([#2579](https://github.com/openchoreo/openchoreo/pull/2579))
- **(API)** Alerting endpoints in observer fixed. ([#2508](https://github.com/openchoreo/openchoreo/pull/2508))
- **(API)** Release generation action check fixed. ([#2688](https://github.com/openchoreo/openchoreo/pull/2688))
- **(API)** Metadata object no longer sent in workflow logs response. ([#2455](https://github.com/openchoreo/openchoreo/pull/2455))
- **(API)** Component schema updated in OpenAPI spec. ([#2649](https://github.com/openchoreo/openchoreo/pull/2649))
- **(API)** Missing workflow kind ref in WorkflowRun OpenAPI spec fixed. ([#2641](https://github.com/openchoreo/openchoreo/pull/2641))
- **(API)** Builds skipped for non-matching branches on webhook events. ([#2519](https://github.com/openchoreo/openchoreo/pull/2519))
- **(Controller)** Workflow kind passed correctly when starting component workflow run. ([#2669](https://github.com/openchoreo/openchoreo/pull/2669))
- **(Controller)** ReleaseBinding Ready condition always set and CrashLoopBackOff detected. ([#2698](https://github.com/openchoreo/openchoreo/pull/2698))
- **(Controller)** Cluster-agent 401 errors after ~1 hour on clusters with bound ServiceAccount tokens (e.g., AKS) fixed. ([#2722](https://github.com/openchoreo/openchoreo/pull/2722))
- **(CLI)** WorkflowRun list no longer always shows Pending status. ([#2654](https://github.com/openchoreo/openchoreo/pull/2654))
- **(CLI)** WorkflowRun creation fixed. ([#2634](https://github.com/openchoreo/openchoreo/pull/2634))
- **(CLI)** Scaffold command fixed to use cluster-scoped resources. ([#2696](https://github.com/openchoreo/openchoreo/pull/2696))
- **(CLI)** Existing release binding handled in deploy flow. ([#2678](https://github.com/openchoreo/openchoreo/pull/2678))
- **(Helm)** Missing property field in external secrets fixed. ([#2452](https://github.com/openchoreo/openchoreo/pull/2452))
- **(Helm)** Missing ClusterWorkflow view permission in backstage catalog reader role fixed. ([#2570](https://github.com/openchoreo/openchoreo/pull/2570))
- **(Helm)** Missing ClusterWorkflow permission in cluster role fixed. ([#2566](https://github.com/openchoreo/openchoreo/pull/2566))
- **(Helm)** Missing ClusterRoles RBAC and ClusterTrait kind in embedded traits sample fixed. ([#2714](https://github.com/openchoreo/openchoreo/pull/2714))
- **(Observability)** Observer and tracing adapter integration fixed. ([#2467](https://github.com/openchoreo/openchoreo/pull/2467))
- **(Observability)** Alert rule GET response fixed to return full alert rule instead of only rule IDs. ([#2552](https://github.com/openchoreo/openchoreo/pull/2552))
- **(Install)** Multiple quick-start and installation fixes. ([#2664](https://github.com/openchoreo/openchoreo/pull/2664), [#2672](https://github.com/openchoreo/openchoreo/pull/2672), [#2685](https://github.com/openchoreo/openchoreo/pull/2685), [#2689](https://github.com/openchoreo/openchoreo/pull/2689), [#2690](https://github.com/openchoreo/openchoreo/pull/2690), [#2692](https://github.com/openchoreo/openchoreo/pull/2692), [#2693](https://github.com/openchoreo/openchoreo/pull/2693))
- **(Backstage UI)** Workflow parameters and type extraction fixed. ([#394](https://github.com/openchoreo/backstage-plugins/pull/394))
- **(Backstage UI)** Workflow kind propagated correctly through build trigger flow. ([#381](https://github.com/openchoreo/backstage-plugins/pull/381))
- **(Backstage UI)** Workflow status handling and UI components fixed. ([#387](https://github.com/openchoreo/backstage-plugins/pull/387))
- **(Backstage UI)** Project dropdown conditionally shown only when namespace is selected. ([#398](https://github.com/openchoreo/backstage-plugins/pull/398))
- **(Backstage UI)** In-app navigation triggered for links in CompactEntityHeader. ([#396](https://github.com/openchoreo/backstage-plugins/pull/396))
- **(Backstage UI)** Release binding status handling and conditions display improved. ([#349](https://github.com/openchoreo/backstage-plugins/pull/349))
- **(Backstage UI)** Glitch effect in traits configuration during component creation wizard fixed. ([#339](https://github.com/openchoreo/backstage-plugins/pull/339))
- **(Backstage UI)** Permission check no longer restricted to default namespace, fixing resource
  visibility in other namespaces. ([#343](https://github.com/openchoreo/backstage-plugins/pull/343))
- **(Backstage UI)** Project-specific deployment pipeline fetched instead of first in namespace. ([#365](https://github.com/openchoreo/backstage-plugins/pull/365))
- **(Backstage UI)** Cluster-scoped kinds restored when cluster scope toggled back on in platform overview. ([#404](https://github.com/openchoreo/backstage-plugins/pull/404))
- **(Backstage UI)** Project-level deny policy now correctly disables UI actions over namespace-level allow. ([#409](https://github.com/openchoreo/backstage-plugins/pull/409))
- **(Backstage UI)** Deployment status uses Ready condition as single source of truth, fixing
  incorrect status display. ([#407](https://github.com/openchoreo/backstage-plugins/pull/407))
- **(Backstage UI)** Cluster workflows not showing in component types fixed. ([#414](https://github.com/openchoreo/backstage-plugins/pull/414))
- **(Backstage UI)** Catalog table column misalignment between header and data rows fixed. ([#413](https://github.com/openchoreo/backstage-plugins/pull/413))
- **(Backstage UI)** Platform Overview scope defaults to first available namespace. ([#412](https://github.com/openchoreo/backstage-plugins/pull/412))
- **(Backstage UI)** Missing deploymentpipeline template in production config fixed. ([#411](https://github.com/openchoreo/backstage-plugins/pull/411))
- **(Backstage UI)** Observability configuration in BuildEvents component fixed. ([#415](https://github.com/openchoreo/backstage-plugins/pull/415))

---

For changes in earlier versions, see [GitHub Releases](https://github.com/openchoreo/openchoreo/releases).



File: install/k3d/registry-cache/README.md
---
# Registry Pull-Through Cache

A Compose setup that runs local pull-through caches for container registries used by OpenChoreo.
This speeds up repeated image pulls during local development.

## How It Works

Each cache is a `registry:2` instance configured as a pull-through proxy for one upstream registry.
On first pull, the image is fetched from the upstream and cached locally. Subsequent pulls (by any
client using the cache) are served from local disk.

```mermaid
flowchart LR
    A[k3d node] -->|pull ghcr.io/openchoreo/controller| B[ghcr-cache :5601]
    B -->|HIT| C[Serve from local disk]
    B -->|MISS| D[Fetch from ghcr.io]
    D --> E[Cache locally]
    E --> C
```

If the caches are not running, containerd falls back to pulling directly from the upstream
registry.

## Ports

| Port | Upstream        |
|------|-----------------|
| 5601 | ghcr.io         |
| 5602 | docker.io       |
| 5603 | quay.io         |
| 5604 | cr.kgateway.dev |

## Quick Start

```bash
# Start all caches
docker compose up -d

# Verify they're running
docker compose ps
```

Then create your k3d cluster with the registry mirrors. Add this to your k3d config's
`registries` section (or pass via `--registry-config`):

```yaml
registries:
  config: |
    mirrors:
      "ghcr.io":
        endpoint:
          - http://host.k3d.internal:5601
      "docker.io":
        endpoint:
          - http://host.k3d.internal:5602
      "quay.io":
        endpoint:
          - http://host.k3d.internal:5603
      "cr.kgateway.dev":
        endpoint:
          - http://host.k3d.internal:5604
```

## Browsing Cached Images

```bash
# List all cached repo:tag pairs
./list-cached.sh

# List only ghcr cache
./list-cached.sh ghcr-cache
```

## Refreshing Mutable Tags

Mutable tags like `latest-dev` get cached on first pull. If upstream publishes a new image
under the same tag, the cache will continue serving the old version.

Use the purge script to invalidate stale images:

```bash
# Purge a specific image:tag
./purge-cache.sh openchoreo/controller:latest-dev

# Purge all tags of a repo
./purge-cache.sh openchoreo/controller

# Purge all openchoreo repos
./purge-cache.sh openchoreo/*

# Purge from any registry (auto-detected)
./purge-cache.sh external-secrets/external-secrets:v2.0.1

# Purge everything from all caches
./purge-cache.sh --all
```

## Cleanup

```bash
# Stop caches (cached data preserved in Docker volumes)
docker compose down

# Stop and clear all cached data
docker compose down -v
```



File: pkg/cli/README.md
---
# Choreo CLI Library

A framework for building consistent and user-friendly command-line interfaces in Go. This guide explains how to use the library to create a new CLI and implement commands.

## Table of Contents
- [Choreo CLI Library](#choreo-cli-library)
    - [Table of Contents](#table-of-contents)
    - [Using the Library](#using-the-library)
        - [1. Create a New CLI Project](#1-create-a-new-cli-project)
        - [2. Create Main Entry Point](#2-create-main-entry-point)
        - [3. Implement Command Interface](#3-implement-command-interface)
    - [Architecture](#architecture)
        - [Core Concepts](#core-concepts)
        - [Implementing a New Command](#implementing-a-new-command)
        - [Best Practices](#best-practices)
        - [Testing Commands](#testing-commands)
        - [Examples](#examples)

## Using the Library

### 1. Create a New CLI Project

```bash
# Initialize a new Go module
go mod init mycli

# Add the Choreo CLI library as a dependency
go get github.com/openchoreo/openchoreo/pkg/cli
```

### 2. Create Main Entry Point
Create ```main.go```:

```go
package main

import (
    "fmt"
    "os"

    "github.com/openchoreo/openchoreo/pkg/cli/common/config"
    "github.com/openchoreo/openchoreo/pkg/cli/core/root"
)

func main() {
    // Initialize config
    cfg := config.DefaultConfig()
    cfg.Name = "mycli"
    cfg.ShortDescription = "My CLI tool"
    
    // Create implementation
    impl := &CommandImplementation{}
    
    // Build root command
    rootCmd := root.BuildRootCmd(cfg, impl)

    // Execute
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
```

### 3. Implement Command Interface
Create ```internal/mycli/impl.go```:

```go
package mycli

import "github.com/openchoreo/openchoreo/pkg/cli/types/api"

type CommandImplementation struct{}

// Implement required interfaces
var _ api.CommandImplementationInterface = &CommandImplementation{}

// Implement interface methods
func (c *CommandImplementation) MyCommand(params api.MyCommandParams) error {
    // Command implementation
    return nil
}
```

## Architecture

```
pkg/cli/
├── cmd/                    # Command implementations
│   ├── apply/             # Apply command 
│   ├── create/            # Create command
│   ├── list/              # List command
│   ├── login/             # Login command
│   └── logout/            # Logout command
├── common/                 # Shared utilities
│   ├── config/            # CLI configuration
│   ├── constants/         # Command definitions
│   ├── messages/          # User-facing messages
│   └── flags/             # Common flag definitions
├── core/                  # Core CLI functionality
│   └── root/             # Root command builder
└── types/                # Interfaces and types
    └── api/             # Command interfaces
```

### Core Concepts

1. **Command Implementation Interface**: All commands implement 

CommandImplementationInterface



2. **User Messages**: All user-facing text is centralized in messages.go

3. **Command Structure**: Commands follow a consistent pattern with:
   - Command definition
   - Flag handling
   - Input validation
   - Error handling

### Implementing a New Command

1. Create a new package under ```cmd:```

```go
package mycommand

import (
    "github.com/spf13/cobra"
    "github.com/openchoreo/openchoreo/pkg/cli/common/constants"
    "github.com/openchoreo/openchoreo/pkg/cli/types/api"
)

func NewMyCommand(impl api.CommandImplementationInterface) *cobra.Command {
    cmd := &cobra.Command{
        Use:   constants.MyCommand.Use,
        Short: constants.MyCommand.Short,
        RunE: func(cmd *cobra.Command, args []string) error {
            return impl.MyCommand(api.MyCommandParams{})
        },
    }
    return cmd
}
```

2. Add command definition in ```definitions.go```:

```go
var MyCommand = Command{
    Use:   "mycommand",
    Short: "My command description",
    Long:  "Detailed description of my command",
}
```

3. Add messages in ```messages.go```:

```go
const (
    ErrMyCommand = "my command failed: %v"
    SuccessMyCommand = "✓ My command completed successfully"
)
```

4. Register command in ```root.go```:

```go
rootCmd.AddCommand(
    mycommand.NewMyCommand(impl),
)
```

### Best Practices

1. **Error Handling**
- ToDo: Introduce errors.go and split the messages.go
- Use typed errors from ```messages.go```
- Include helpful error hints
- Clean up resources on error

2. **User Experience**
- flag-based mode
- Add command examples and help text
- Use consistent output formatting

3. **Code Organization**
- Keep command logic in separate packages
- Reuse common flags and utilities
- Follow existing patterns

### Testing Commands

//ToDo

### Examples

See existing commands for reference implementations:
- list.go - Table output, YAML output
- create.go - Resource creation with validation
- apply.go - File handling and error management

For more details on the CLI architecture and implementation, see the code documentation in each package.



File: install/k3d/single-cluster/README.md
---
# Single-Cluster Setup

All-in-one OpenChoreo setup with all planes running in a single k3d cluster.

> [!NOTE]
> This guide is for **contributors and developers** working from a local checkout.
> It uses local Helm charts (`install/helm/...`) and standalone setup scripts.
> If you just want to try OpenChoreo, follow the [public getting-started guide](https://openchoreo.dev/docs/getting-started/try-it-out/on-k3d-locally/) instead, which uses published OCI chart releases.

> [!IMPORTANT]
> If you're using Colima, set `K3D_FIX_DNS=0` when creating clusters.
> See [k3d-io/k3d#1449](https://github.com/k3d-io/k3d/issues/1449).

## 1. Create Cluster

```bash
k3d cluster create --config install/k3d/single-cluster/config.yaml

docker exec k3d-openchoreo-server-0 sh -c \
  "cat /proc/sys/kernel/random/uuid | tr -d '-' > /etc/machine-id"
```

> [!TIP]
> For faster setup, consider using [Image Preloading](#image-preloading) after creating the cluster.

## 2. Install Prerequisites

### Gateway API CRDs

```bash
kubectl apply --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/experimental-install.yaml
```

### cert-manager

```bash
helm upgrade --install cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.19.4 \
  --set crds.enabled=true
```

```bash
kubectl wait --for=condition=Available deployment/cert-manager \
  -n cert-manager --timeout=180s
```

### External Secrets Operator

```bash
helm upgrade --install external-secrets oci://ghcr.io/external-secrets/charts/external-secrets \
  --namespace external-secrets \
  --create-namespace \
  --version 2.0.1 \
  --set installCRDs=true
```

```bash
kubectl wait --for=condition=Available deployment/external-secrets \
  -n external-secrets --timeout=180s
```

### kgateway

Single install, watches Gateway resources across all namespaces.

```bash
helm upgrade --install kgateway-crds oci://cr.kgateway.dev/kgateway-dev/charts/kgateway-crds \
  --create-namespace --namespace openchoreo-control-plane \
  --version v2.2.1

helm upgrade --install kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
  --namespace openchoreo-control-plane --create-namespace \
  --version v2.2.1 \
  --set controller.extraEnv.KGW_ENABLE_GATEWAY_API_EXPERIMENTAL_FEATURES=true
```

## 3. Setup Control Plane

### Thunder (Identity Provider)

Bootstrap scripts auto-configure the org, users, groups, and OAuth apps on first startup.

```bash
helm upgrade --install thunder oci://ghcr.io/asgardeo/helm-charts/thunder \
  --namespace thunder \
  --create-namespace \
  --version 0.28.0 \
  --values install/k3d/common/values-thunder.yaml
```

### CoreDNS Rewrite

```bash
kubectl apply -f install/k3d/common/coredns-custom.yaml
```

### Backstage Secrets

```bash
kubectl create namespace openchoreo-control-plane --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic backstage-secrets \
  -n openchoreo-control-plane \
  --from-literal=backend-secret="$(head -c 32 /dev/urandom | base64)" \
  --from-literal=client-secret="backstage-portal-secret" \
  --from-literal=jenkins-api-key="placeholder-not-in-use"
```

### Install Control Plane

```bash
helm upgrade --install openchoreo-control-plane install/helm/openchoreo-control-plane \
  --namespace openchoreo-control-plane \
  --create-namespace \
  --values install/k3d/single-cluster/values-cp.yaml
```

```bash
kubectl wait -n openchoreo-control-plane \
  --for=condition=available --timeout=300s deployment --all
```

### Extract Cluster Gateway CA

Wait for cert-manager to issue the cluster-gateway CA certificate, then populate the ConfigMap that the controller-manager and cluster-agents use to verify the gateway server.

```bash
# Wait for the cert-manager secret to be ready
kubectl wait -n openchoreo-control-plane \
  --for=condition=Ready certificate/cluster-gateway-ca --timeout=120s

# Extract the public CA cert into the ConfigMap
kubectl get secret cluster-gateway-ca -n openchoreo-control-plane \
  -o jsonpath='{.data.ca\.crt}' | base64 -d | \
  kubectl create configmap cluster-gateway-ca \
    --from-file=ca.crt=/dev/stdin \
    -n openchoreo-control-plane \
    --dry-run=client -o yaml | kubectl apply -f -
```

## 4. Install Default Resources

```bash
kubectl apply -f samples/getting-started/all.yaml
kubectl label namespace default openchoreo.dev/control-plane=true --overwrite
```

## 5. Setup Data Plane

### Namespace and Certificates

```bash
kubectl create namespace openchoreo-data-plane --dry-run=client -o yaml | kubectl apply -f -

# Copy cluster-gateway CA (public cert only) so the agent can verify the gateway server
CA_CRT=$(kubectl get configmap cluster-gateway-ca \
  -n openchoreo-control-plane -o jsonpath='{.data.ca\.crt}')

kubectl create configmap cluster-gateway-ca \
  --from-literal=ca.crt="$CA_CRT" \
  -n openchoreo-data-plane \
  --dry-run=client -o yaml | kubectl apply -f -
```

### OpenBao (Secret Store)

Install [OpenBao](https://openbao.org/) as the secret backend and create a `ClusterSecretStore` named `default`:

```bash
install/prerequisites/openbao/setup.sh --dev --seed-dev-secrets
```

This installs OpenBao in dev mode into the `openbao` namespace, configures Kubernetes auth with reader/writer policies, seeds placeholder development secrets, and creates the `ClusterSecretStore`.

To use a different secret backend (Vault, AWS Secrets Manager, etc.), skip this step and create your own `ClusterSecretStore` named `default` following the [ESO provider docs](https://external-secrets.io/latest/provider/).

### Install Data Plane

```bash
helm upgrade --install openchoreo-data-plane install/helm/openchoreo-data-plane \
  --dependency-update \
  --namespace openchoreo-data-plane \
  --create-namespace \
  --values install/k3d/single-cluster/values-dp.yaml
```

### Register Data Plane

```bash
AGENT_CA=$(kubectl get secret cluster-agent-tls \
  -n openchoreo-data-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterDataPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  secretStoreRef:
    name: default
  gateway:
    ingress:
      external:
        http:
          host: openchoreoapis.localhost
          listenerName: http
          port: 19080
        name: gateway-default
        namespace: openchoreo-data-plane
EOF
```

## 6. Setup Workflow Plane (Optional)

### Namespace and Certificates

```bash
kubectl create namespace openchoreo-workflow-plane --dry-run=client -o yaml | kubectl apply -f -

# Copy cluster-gateway CA (public cert only) so the agent can verify the gateway server
CA_CRT=$(kubectl get configmap cluster-gateway-ca \
  -n openchoreo-control-plane -o jsonpath='{.data.ca\.crt}')

kubectl create configmap cluster-gateway-ca \
  --from-literal=ca.crt="$CA_CRT" \
  -n openchoreo-workflow-plane \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Container Registry

```bash
helm repo add twuni https://twuni.github.io/docker-registry.helm
helm repo update

helm install registry twuni/docker-registry \
  --namespace openchoreo-workflow-plane \
  --create-namespace \
  --values install/k3d/single-cluster/values-registry.yaml
```

### Install Workflow Plane

```bash
helm upgrade --install openchoreo-workflow-plane install/helm/openchoreo-workflow-plane \
  --dependency-update \
  --namespace openchoreo-workflow-plane \
  --values install/k3d/single-cluster/values-wp.yaml
```

### Workflow Templates

The build pipeline is composed of shared ClusterWorkflowTemplates that each handle one step (checkout, build, publish, generate workload). The checkout and publish templates are applied separately so you can replace them to use your own git auth or container registry.

```bash
kubectl apply -f samples/getting-started/workflow-templates/checkout-source.yaml
kubectl apply -f samples/getting-started/workflow-templates.yaml
kubectl apply -f samples/getting-started/workflow-templates/publish-image-k3d.yaml
kubectl apply -f samples/getting-started/workflow-templates/generate-workload-k3d.yaml
```

`publish-image-k3d.yaml` pushes images to the local k3d registry at `host.k3d.internal:10082`. To use a different registry, replace this with your own `publish-image` ClusterWorkflowTemplate.

### Buildpack Cache (Optional)

Pre-populates the local registry with buildpack images so Ballerina and Google Cloud Buildpacks workflows don't pull from remote registries on every build. Skip this if you only use Docker or React builds.

```bash
kubectl apply -f install/k3d/common/push-buildpack-cache-images.yaml
```

### Register Workflow Plane

```bash
AGENT_CA=$(kubectl get secret cluster-agent-tls \
  -n openchoreo-workflow-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterWorkflowPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  secretStoreRef:
    name: default
EOF
```

## 7. Setup Observability Plane (Optional)

### Namespace and Certificates

```bash
kubectl create namespace openchoreo-observability-plane --dry-run=client -o yaml | kubectl apply -f -

# Copy cluster-gateway CA (public cert only) so the agent can verify the gateway server
CA_CRT=$(kubectl get configmap cluster-gateway-ca \
  -n openchoreo-control-plane -o jsonpath='{.data.ca\.crt}')

kubectl create configmap cluster-gateway-ca \
  --from-literal=ca.crt="$CA_CRT" \
  -n openchoreo-observability-plane \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Observability Plane Secrets

```bash
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: observer-secret
  namespace: openchoreo-observability-plane
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: default
  target:
    name: observer-secret
  data:
  - secretKey: OPENSEARCH_USERNAME
    remoteRef:
      key: opensearch-username
      property: value
  - secretKey: OPENSEARCH_PASSWORD
    remoteRef:
      key: opensearch-password
      property: value
  - secretKey: UID_RESOLVER_OAUTH_CLIENT_SECRET
    remoteRef:
      key: observer-oauth-client-secret
      property: value
EOF

kubectl wait -n openchoreo-observability-plane \
  --for=condition=Ready externalsecret/observer-secret --timeout=60s
```

### Install Observability Plane

```bash
helm upgrade --install openchoreo-observability-plane install/helm/openchoreo-observability-plane \
  --dependency-update \
  --namespace openchoreo-observability-plane \
  --values install/k3d/single-cluster/values-op.yaml \
  --timeout 10m
```

#### Install Observability Modules

Install the required logs, metrics and tracing modules. Refer https://openchoreo.dev/modules for more details

```bash
kubectl wait -n openchoreo-observability-plane \
  --for=condition=available --timeout=600s deployment --all
```

### Register Observability Plane

```bash
AGENT_CA=$(kubectl get secret cluster-agent-tls \
  -n openchoreo-observability-plane -o jsonpath='{.data.ca\.crt}' | base64 -d)

kubectl apply -f - <<EOF
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterObservabilityPlane
metadata:
  name: default
spec:
  planeID: default
  clusterAgent:
    clientCA:
      value: |
$(echo "$AGENT_CA" | sed 's/^/        /')
  observerURL: http://observer.openchoreo.localhost:11080
EOF
```

### Link Other Planes

```bash
kubectl patch clusterdataplane default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'

# If cluster workflow plane is installed:
kubectl patch clusterworkflowplane default -n default --type merge \
  -p '{"spec":{"observabilityPlaneRef":{"kind":"ClusterObservabilityPlane","name":"default"}}}'
```

## Port Mappings

All ports are mapped 1:1 (host:container) unless noted.

| Port  | Plane         | Service                |
|-------|---------------|------------------------|
| 8080  | Control       | Gateway HTTP           |
| 8443  | Control       | Gateway HTTPS          |
| 19080 | Data          | Gateway HTTP           |
| 19443 | Data          | Gateway HTTPS          |
| 10081 | Build         | Argo Workflows UI      |
| 10082 | Build         | Container Registry     |
| 11080 | Observability | Observer API (HTTP)    |
| 11085 | Observability | Gateway HTTPS          |
| 11081 | Observability | OpenSearch Dashboards* |
| 11082 | Observability | OpenSearch API*        |

*OpenSearch ports are not 1:1 (11081:5601, 11082:9200) since those services don't support port overrides.

## Access Services

| Service              | URL                                           |
|----------------------|-----------------------------------------------|
| OpenChoreo Console   | http://openchoreo.localhost:8080               |
| OpenChoreo API       | http://api.openchoreo.localhost:8080           |
| Thunder Admin        | http://thunder.openchoreo.localhost:8080       |
| Argo Workflows UI    | http://localhost:10081                         |
| Observer API         | http://observer.openchoreo.localhost:11080     |

## Verification

```bash
# All pods
kubectl get pods -n openchoreo-control-plane
kubectl get pods -n openchoreo-data-plane
kubectl get pods -n openchoreo-workflow-plane
kubectl get pods -n openchoreo-observability-plane

# Plane resources
kubectl get clusterdataplane,clusterworkflowplane,clusterobservabilityplane -n default

# Agent connections
kubectl logs -n openchoreo-data-plane -l app=cluster-agent --tail=5
kubectl logs -n openchoreo-workflow-plane -l app=cluster-agent --tail=5
kubectl logs -n openchoreo-observability-plane -l app=cluster-agent --tail=5
```

## Image Preloading

Pull images to your host first, then import into the cluster. Useful for slow networks or frequent cluster recreation.

```bash
# All planes
install/k3d/preload-images.sh \
  --cluster openchoreo \
  --local-charts \
  --control-plane --cp-values install/k3d/single-cluster/values-cp.yaml \
  --data-plane --dp-values install/k3d/single-cluster/values-dp.yaml \
  --workflow-plane --wp-values install/k3d/single-cluster/values-wp.yaml \
  --observability-plane --op-values install/k3d/single-cluster/values-op.yaml \
  --parallel 4
```

Run after creating the cluster but before installing anything.

## Cleanup

```bash
k3d cluster delete openchoreo
```



File: samples/component-types/component-with-configs/README.md
---
# Component with Configurations Sample

This sample demonstrates how to deploy a component with environment variables, config files, and secrets in OpenChoreo.

## Overview

This sample includes the following OpenChoreo Custom Resources:

### ComponentType (`service-with-configs`)

Defines a reusable component type template based on the default `deployment/service` structure that supports configurations. It:

- Specifies the workload type as `deployment`
- Follows the standard service ComponentType structure with:
  - Allowed workflows (google-cloud-buildpacks, ballerina-buildpack, docker)
  - Allowed traits (observability-alert-rule)
  - Validation rules for service endpoints
- Defines a schema with:
  - Environment-specific overrides: `replicas`, `resources`, `imagePullPolicy`
- Templates the underlying Kubernetes resources (Deployment, Service, HTTPRoute, ConfigMaps, ExternalSecrets)
- Automatically creates ConfigMaps for environment variables and file mounts
- Automatically creates ExternalSecrets for secret environment variables and secret files
- Uses CEL expressions to dynamically populate values from component metadata, parameters, and configurations

### SecretReference (`database-secret`, `github-pat-secret`)

Defines references to external secrets that can be used by components:

- `database-secret`: References a database password from an external secret store
- `github-pat-secret`: References a GitHub personal access token from an external secret store

### Component (`demo-app`)

Defines the actual component using the `service-with-configs` type. It:

- References the `deployment/service-with-configs` component type
- Enables auto-deployment to environments
- Belongs to the `default` project

### Workload (`demo-app-workload`)

Specifies the container image and configuration for the component:

- Links to the `demo-app` component
- Defines the container image (`nginx:1.25-alpine`)
- Configures environment variables:
  - `LOG_LEVEL`: Plain text value
  - `DATABASE_PASSWORD`: Value from secret reference
- Configures file mounts:
  - `application.toml`: Plain text config file mounted at `/conf`
  - `gitPAT`: Secret file mounted at `/conf` from secret reference

### ReleaseBinding (`demo-app-development`)

Represents a deployment of the component in a specific environment. It:

- Links to the `demo-app` component
- Targets the `development` environment
- Provides ComponentType environment-specific overrides:
  - Replicas: 2
  - Resource requests/limits (CPU and memory)
- Provides workload overrides for environment-specific configurations:
  - Additional environment variables (`FEATURE_FLAG`, `NEW_ENV_VAR`)
  - Environment-specific file content overrides (overriding `application.toml`)

## Key Features

This sample demonstrates the comprehensive configuration capabilities available in OpenChoreo ComponentTypes:

- **Environment Variables**: Both plain text and secret-backed values
- **Config Files**: Plain text configuration files mounted into containers
- **Secret Files**: Secret-backed files (e.g., credentials, tokens) mounted into containers
- **Environment-Specific Overrides**: Different configurations per environment via ReleaseBinding

> **Note**: The default `deployment/service` ComponentType already includes all these configuration capabilities. This sample uses a custom ComponentType (`deployment/service-with-configs`) following the same structure to explicitly demonstrate configuration features.

## How It Works

1. **ComponentType** acts as a template/blueprint that handles configurations and includes:
   - Standard Deployment and Service resources
   - HTTPRoute resources for endpoints with `external` or `internal` visibility
   - Automatic ConfigMap creation for environment variables and files
   - Automatic ExternalSecret creation for secret environment variables and files
2. **SecretReference** defines how to fetch secrets from external secret stores
3. **Component** uses that template and provides base configuration
4. **Workload** specifies what container(s) to run and their configurations (env vars, files, secrets)
5. **ReleaseBinding** specifies the actual deployment with environment-specific overrides

The OpenChoreo controller manager uses these resources and generates the Kubernetes resources (Deployment, Service, HTTPRoute, ConfigMaps, ExternalSecrets) based on the templates and parameters.

## Deploy the sample

Apply the sample:

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-with-configs/component-with-configs.yaml
```

## Check the ReleaseBinding status

```bash
kubectl get releasebinding demo-app-development -o yaml | grep -A 50 "^status:"
```

## Verify Generated Resources

### Check ConfigMaps

```bash
kubectl get configmap -A -l openchoreo.dev/component=demo-app
```

### Check ExternalSecrets

```bash
kubectl get externalsecret -A -l openchoreo.dev/component=demo-app
```

### Check Deployment

```bash
kubectl get deployment -A -l openchoreo.dev/component=demo-app
```

## Verify Environment Variables and Config Files in Pod

Once the pods are running, you can verify that environment variables and config files are correctly injected.

### Get a pod name

```bash
POD_NAMESPACE=$(kubectl get deployment -A -l openchoreo.dev/component=demo-app -o jsonpath='{.items[0].metadata.namespace}')
POD_NAME=$(kubectl get pods -n $POD_NAMESPACE -o jsonpath='{.items[0].metadata.name}')
```

### Verify environment variables are injected

```bash
kubectl exec -n $POD_NAMESPACE $POD_NAME -- env | grep -E "LOG_LEVEL|FEATURE_FLAG|NEW_ENV_VAR"
```

Expected output:

```text
FEATURE_FLAG=true
LOG_LEVEL=info
NEW_ENV_VAR=new_value
```

### Verify config file is mounted

```bash
kubectl exec -n $POD_NAMESPACE $POD_NAME -- cat /conf/application.toml
```

Expected output:

```text
schema_generation:
  enable: false
```

## Cleanup

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-with-configs/component-with-configs.yaml
```

## Troubleshooting

If the application is not accessible or resources are not created:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding demo-app-development -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding demo-app-development -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=demo-app
   ```

4. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=demo-app -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=demo-app --tail=50
   ```

5. **Verify ConfigMaps are created:**
   ```bash
   kubectl get configmap -A -l openchoreo.dev/component=demo-app -o yaml
   ```

6. **Verify ExternalSecrets status:**
   ```bash
   kubectl get externalsecret -A -l openchoreo.dev/component=demo-app -o yaml
   ```

7. **Check if secrets are synced:**
   ```bash
   kubectl get secret -A -l openchoreo.dev/component=demo-app
   ```



File: samples/from-image/echo-websocket-service/README.md
---
# Echo WebSocket Service (From Image)

## Overview

This sample demonstrates how to deploy a WebSocket echo service in OpenChoreo from a pre-built container image. The service accepts WebSocket connections and echoes back any messages sent to it.

The service is deployed from the pre-built image:
`jmalloc/echo-server:latest`

### WebSocket Endpoint

**Endpoint:** `/.ws`
**Protocol:** WebSocket
**Functionality:** Echoes back any message sent by the client.

## Step 1: Enable WebSockets at the Ingress Gateway

Before deploying the WebSocket service, you need to enable WebSocket upgrades at the ingress gateway by applying the following HTTPListenerPolicy:

```bash
kubectl apply -f - <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: default-httplistenerpolicy
  namespace: openchoreo-data-plane
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: gateway-default
  upgradeConfig:
    enabledUpgrades:
    - websocket
EOF
```

## Step 2: Deploy the Application

The following command will create the relevant resources in OpenChoreo:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/echo-websocket-service/echo-websocket-service.yaml
```

> [!NOTE]
> Since this uses a pre-built image, the deployment will be faster compared to building from source.

## Step 3: Test the Application

You can test the WebSocket service using `wscat` (install via `npm install -g wscat`).

### Connect to the WebSocket

The service is exposed at the base path `/{component-name}-{endpoint-name}`. For this sample, the component name is `echo-websocket-service` and endpoint name is `websocket`.

```bash
wscat -c "ws://localhost:19080/echo-websocket-service-websocket/.ws" --header "Host: development-default.openchoreoapis.localhost"
```

Once connected, type any message and press Enter. The server will echo back the same message.

### Example Session

```
Connected (press CTRL+C to quit)
> Hello, WebSocket!
< Hello, WebSocket!
> Test message
< Test message
```

## Troubleshooting Service Access Issues

If you cannot access the service:

1. Check if the ReleaseBinding is ready:
   ```bash
   kubectl get releasebinding echo-websocket-service-development -n default -o yaml
   ```

2. Check the ReleaseBinding status conditions:
   ```bash
   kubectl get releasebinding echo-websocket-service-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. Verify the HTTPRoute is configured correctly:
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=echo-websocket-service -o yaml
   ```

4. Check the deployment status:
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=echo-websocket-service
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/echo-websocket-service/echo-websocket-service.yaml
```



File: install/quick-start/README.md
---
# OpenChoreo Quick-Start

A containerized environment to quickly try OpenChoreo without installing any tools on your machine. Everything you need
is pre-configured inside a Docker container.

## What's Included

- **Pre-installed Tools**: k3d, kubectl and helm
- **Interactive Environment**: Bash shell with helpful aliases and auto-completion
- **Sample Applications**: Ready-to-deploy examples to explore OpenChoreo capabilities
- **Installation Scripts**: Automated setup for local k3d cluster with OpenChoreo
- **Optional Workflow Plane**: Argo Workflows + Container Registry for building from source

## Prerequisites

- Docker

## Getting Started

### 1. Start the Quick-Start Container

Run the following command to start the containerized environment:

```bash
docker run -it --rm \
  --name openchoreo-quick-start \
  --privileged \
  --network=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/openchoreo/quick-start:latest
```

**Important:** The `--privileged` flag is required for k3d to run properly inside the container (Docker-in-Docker with containerd). This is especially necessary when using Colima or other container runtimes with cgroup v2.

**Available Tags:**

- `latest` - Latest stable release
- `latest-dev` - Latest development build
- `v0.4.0` - Specific release version

You'll see a welcome message with quick commands to get started.

### 2. Install OpenChoreo

Inside the container, run the installation script:

```bash
./install.sh
```

Installation typically takes 5-10 minutes depending on your network speed.

**Installation Options:**

- `./install.sh` - Install with Control Plane and Data Plane (minimal setup)
- `./install.sh --with-build` - Install with Workflow Plane (Argo Workflows + Container Registry)
- `./install.sh --with-observability` - Install with OpenSearch and observability components
- `./install.sh --with-build --with-observability` - Install full platform with all optional components
- `./install.sh --version v0.4.0` - Install a specific OpenChoreo version
- `./install.sh --version latest-dev --debug` - Install latest development build with verbose logging
- `./install.sh --skip-preload` - Skip image preloading from local Docker to k3d
- `./install.sh --debug` - Enable verbose logging
- `./install.sh --help` - Show all available options

The installer will:

- Create a local k3d Kubernetes cluster
- Install OpenChoreo Control Plane
- Install OpenChoreo Data Plane
- Optionally install Workflow Plane (for building from source)
- Optionally install Observability Plane (for monitoring and logs)
- Configure the environment for sample deployments

### 3. Try a Sample Application

After installation completes, deploy a sample application to see OpenChoreo in action.

#### Deploy from Pre-built Images

**Simple React Web Application:**

```bash
./deploy-react-starter.sh
```

A lightweight single-component application to quickly verify your setup.

**GCP Microservices Demo (11 Services):**

```bash
./deploy-gcp-demo.sh
```

A complex microservices application demonstrating multi-component deployments with service-to-service communication.

#### Build and Deploy from Source (Requires --with-build)

**Go Greeter Service:**

```bash
./build-deploy-greeter.sh
```

Demonstrates the complete build-to-deploy workflow:
- Clones source code from GitHub
- Builds a Docker image using the Workflow Plane
- Pushes the image to the container registry
- Deploys the service to the Data Plane

The deployment scripts will show you the application URLs when ready.

## Exploring Further

**Browse Sample Applications:**

```bash
ls samples/
```

Explore additional sample applications and deployment configurations.

## Troubleshooting

### k3d Cluster Creation Stuck

If the k3d cluster creation gets stuck at "Injecting records for hostAliases..." or "Waiting for containerd startup", this usually means:

**Solution:** Ensure you started the container with the `--privileged` flag:

```bash
docker run -it --rm \
  --name openchoreo-quick-start \
  --privileged \
  --network=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/openchoreo/quick-start:latest
```

If the cluster is already broken, delete it and recreate:

```bash
k3d cluster delete openchoreo-quick-start
./install.sh
```

### Cluster Agent Pod Stuck in Pending

In single-cluster setups, the cluster agent should start automatically after Helm completes the installation. The Helm post-install jobs automatically:
- Copy the cluster-gateway CA from control plane to data/workflow plane namespaces
- Create TLS certificates for secure communication

If the agent pod is stuck, check the Helm job logs:

```bash
kubectl get jobs -n openchoreo-data-plane
kubectl logs job/<job-name> -n openchoreo-data-plane
```

## Cleaning Up

**Remove a Sample Application:**

```bash
./deploy-react-starter.sh --clean
./deploy-gcp-demo.sh --clean
./build-deploy-greeter.sh --clean
```

**Uninstall OpenChoreo:**

```bash
./uninstall.sh
```

This removes the k3d cluster and all OpenChoreo components.

**Exit the Container:**

```bash
exit
```

The container will be automatically removed (thanks to the `--rm` flag).



File: internal/dataplane/kubernetes/types/README.md
---
# kubernetes/types

This package contains resource type definitions for the Kubernetes integration that are derived from the following projects:
- Cilium: https://github.com/cilium/cilium/tree/main/pkg/k8s/apis/cilium.io
- Argo Workflow: https://github.com/argoproj/argo-workflows/tree/main/pkg/apis/workflow

The original code has been modified to fit the needs of this project.



File: rca-agent/README.md
---
# RCA Agent for OpenChoreo

An autonomous Root Cause Analysis agent that investigates alerts using observability data and LLMs.

## Architecture

### Overview

The RCA agent receives alerts via a REST API, then uses a **ReAct (Reasoning + Acting)** loop to investigate by querying observability data through MCP servers. It produces a structured RCA report with root causes, evidence, and recommendations.

When the experimental auto-remediation feature is enabled, a remediation agent runs after the RCA agent to review, revise, and apply recommended actions.

### MCP Integration

The agent connects to two MCP (Model Context Protocol) servers:
- **Observability MCP** – provides tools for traces, logs, and metrics
- **OpenChoreo MCP** – provides tools for projects, environments, and components

Only a whitelisted set of read-only tools are exposed to the agent, preventing unintended modifications and limiting scope to investigation.

### Middleware

Output middleware intercepts tool responses and transforms raw data before it reaches the LLM — computing metric statistics, detecting anomalies, building trace hierarchies, and grouping logs by component.

### API

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/agent/rca` | Queue an RCA analysis as a background task |
| `POST /api/v1/agent/chat` | Streaming chat for follow-up questions about a report |
| `GET /api/v1/rca-reports/projects/{id}` | List reports by project |
| `GET /api/v1/rca-reports/alerts/{id}` | Get a report by alert |

## Local Development

The following instructions are for local development. For deploying on OpenChoreo, refer docs.

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** package manager
- **LLM API access** - We recommend the latest models from OpenAI or Anthropic for best results
- **OpenSearch cluster** - Port-forward the OpenSearch service to your local machine
- **MCP servers** - Port-forward both the OpenChoreo MCP server and OpenChoreo Observability MCP server to your local machine

### Configuration

| Variable | Description |
|----------|-------------|
| `RCA_LLM_API_KEY` | API key for your LLM provider |
| `RCA_MODEL_NAME` | Model name to use for analysis |
| `OPENSEARCH_ADDRESS` | OpenSearch cluster address |
| `OPENSEARCH_USERNAME` | OpenSearch username |
| `OPENSEARCH_PASSWORD` | OpenSearch password |
| `CONTROL_PLANE_URL` | OpenChoreo control plane URL (MCP URL derived from this) |
| `OBSERVER_MCP_URL` | OpenChoreo Observability MCP server URL |
| `REMED_AGENT` | Enable remediation agent (default: false) |

### Authentication (Optional)

If authentication is enabled, create an OAuth2 client credentials grant and configure:

| Variable | Description |
|----------|-------------|
| `OAUTH_TOKEN_URL` | OAuth2 token endpoint URL |
| `OAUTH_CLIENT_ID` | OAuth2 client ID |
| `OAUTH_CLIENT_SECRET` | OAuth2 client secret |

### Setup

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
fastapi dev src/main.py
```



File: samples/from-image/go-greeter-service/README.md
---
# Go Greeter Service (From Image)

## Overview

This sample demonstrates how to deploy a Go REST service in OpenChoreo from a pre-built container image. The service exposes REST endpoints for greeting functionality and uses a containerized deployment approach.

The service is deployed from the pre-built image:
`ghcr.io/openchoreo/samples/greeter-service:latest`

Exposed REST endpoints:

### Greet a user

**Endpoint:** `/greeter/greet`
**Method:** `GET`
**Functionality:** Sends a greeting to the user.

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/go-greeter-service/greeter-service.yaml
```

> [!NOTE]
> Since this uses a pre-built image, the deployment will be faster compared to building from source.

## Step 2: Test the Application

First, get the service URL from the HTTPRoute:

```bash
# Get the hostname and path prefix from the HTTPRoute
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=greeter-service -o jsonpath='{.items[0].spec.hostnames[0]}')
PATH_PREFIX=$(kubectl get httproute -A -l openchoreo.dev/component=greeter-service -o jsonpath='{.items[0].spec.rules[0].matches[0].path.value}')
```

### Basic Greet
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/greeter/greet"
```

### Greet with name
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/greeter/greet?name=Alice"
```

### Example with direct URL (base path is /{component-name})
The service is exposed at the base path `/{component-name}-{endpoint-name}`. For this sample, the component name is `greeter-service`.

```bash
curl http://development-default.openchoreoapis.localhost:19080/greeter-service-http/greeter/greet
```

## Troubleshooting Service Access Issues

If you cannot access the service:

1. Check if the ReleaseBinding is ready:
   ```bash
   kubectl get releasebinding greeter-service-development -n default -o yaml
   ```

2. Check the ReleaseBinding status conditions:
   ```bash
   kubectl get releasebinding greeter-service-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. Verify the HTTPRoute is configured correctly:
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=greeter-service -o yaml
   ```

4. Check the deployment status:
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=greeter-service
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/go-greeter-service/greeter-service.yaml
```



File: samples/from-image/issue-reporter-schedule-task/README.md
---
# GitHub Issue Reporter Scheduled Task (From Image)

## Overview

This sample demonstrates how to deploy a GitHub Issue Reporter as a scheduled task in OpenChoreo from a pre-built container image. The scheduled task runs periodically to report GitHub issues and integrates with MySQL database and email notifications.

The scheduled task is deployed from the pre-built image:
`ghcr.io/openchoreo/samples/github-issue-reporter:latest`

Features:
- **GitHub Integration**: Connects to GitHub repositories to fetch issue data
- **Database Storage**: Stores issue data in MySQL database
- **Email Notifications**: Sends email reports about GitHub issues
- **Configurable Schedule**: Runs every minute (configurable via CronJob schedule)

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo:

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/issue-reporter-schedule-task/github-issue-reporter.yaml
```

> [!NOTE]
> Since this uses a pre-built image, the deployment will be faster compared to building from source.

## Step 2: Monitor the Scheduled Task

Check the status of the scheduled task and its job executions:

```bash
# View the CronJob created by the scheduled task
kubectl get cronjob -A -l openchoreo.dev/component=github-issue-reporter

# Monitor job executions
kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter

# View logs from the latest job pod
POD_NAMESPACE=$(kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter -o jsonpath='{.items[0].metadata.namespace}')
JOB_NAME=$(kubectl get jobs -n $POD_NAMESPACE -l openchoreo.dev/component=github-issue-reporter --sort-by=.metadata.creationTimestamp --no-headers | tail -1 | awk '{print $1}')
POD_NAME=$(kubectl get pods -n $POD_NAMESPACE -l job-name=$JOB_NAME -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n $POD_NAMESPACE $POD_NAME --tail=50
```

## Configuration

The scheduled task requires several environment variables to be configured:

### GitHub Configuration
- `GITHUB_REPOSITORY`: Target GitHub repository URL
- `GITHUB_TOKEN`: GitHub personal access token for API access

### MySQL Configuration  
- `MYSQL_HOST`: MySQL server hostname
- `MYSQL_PORT`: MySQL server port (default: 3306)
- `MYSQL_USER`: Database username
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name

### Email Configuration
- `EMAIL_HOST`: SMTP server hostname
- `EMAIL_PORT`: SMTP server port (default: 587)
- `EMAIL_SENDER`: Email sender address
- `EMAIL_PASSWORD`: Email account password
- `EMAIL_TO`: Email recipient address

> [!IMPORTANT]
> The current configuration uses hardcoded values for demonstration. In production, use Kubernetes secrets or external secret management systems.

## Troubleshooting

If the scheduled task is not working correctly:

1. **Check the ReleaseBinding status:**
   ```bash
   kubectl get releasebinding github-issue-reporter-development -n default -o yaml
   ```

2. **Check the ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding github-issue-reporter-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify the CronJob is created:**
   ```bash
   kubectl get cronjob -A -l openchoreo.dev/component=github-issue-reporter -o yaml
   ```

4. **Check recent job executions:**
   ```bash
   kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter --sort-by=.metadata.creationTimestamp
   ```

5. **View job logs for debugging:**
   ```bash
   # Get the latest job name
   JOB_NAME=$(kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

   # Get the namespace of the job
   JOB_NAMESPACE=$(kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.namespace}')

   # View logs
   kubectl logs -n $JOB_NAMESPACE job/$JOB_NAME
   ```

6. **Check for failed jobs:**
   ```bash
   kubectl get jobs -A -l openchoreo.dev/component=github-issue-reporter --field-selector status.successful!=1
   ```

## Schedule Configuration

The task is configured to run every minute (`*/1 * * * *`) for testing purposes. To modify the schedule:

1. Edit the `Component` resource in the YAML file
2. Update the `parameters.schedule` field with a valid cron expression
3. Apply the changes using `kubectl apply -f github-issue-reporter.yaml`

Example schedules:
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1-5` - Every weekday at 9 AM
- `0 0 */3 * *` - Every 3 days at midnight

You can also override the schedule for specific environments by modifying the `ReleaseBinding` resource and adding the schedule to the `componentTypeEnvironmentConfigs` section (as shown in the sample YAML where the development environment overrides the schedule to run every 5 minutes).

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/issue-reporter-schedule-task/github-issue-reporter.yaml
```



File: samples/from-image/react-starter-web-app/README.md
---
# React Starter Web Application (From Image)

## Overview

This sample demonstrates how to deploy a React web application in OpenChoreo from a pre-built container image. The application uses a production-ready React SPA served on port 8080.

The application is deployed from the pre-built image:
`choreoanonymouspullable.azurecr.io/react-spa:v0.9`

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/react-starter-web-app/react-starter.yaml
```

> [!NOTE]
> Since this uses a pre-built image, the deployment will be faster compared to building from source.

## Step 2: Access the Application

Once the application is deployed, you can access the React application at:

```
http://http-react-starter-development-default-cde5190f.openchoreoapis.localhost:19080
```

You can also dynamically get the URL using:

```bash
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=react-starter -o jsonpath='{.items[0].spec.hostnames[0]}')
echo "Access the application at: http://${HOSTNAME}:19080"
```

## Troubleshooting Access Issues

If you cannot access the application:

1. **Check if the ReleaseBinding is ready:**
   ```bash
   kubectl get releasebinding react-starter-development -n default -o yaml
   ```

2. **Check the ReleaseBinding status conditions:**
   ```bash
   kubectl get releasebinding react-starter-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify the HTTPRoute is configured correctly:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=react-starter -o yaml
   ```

4. **Check the deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=react-starter
   ```

5. **Check pod logs for errors:**
   ```bash
   POD_UUID=$(kubectl get pods -A -l "$(kubectl get deploy -A -l openchoreo.dev/component=react-starter -o jsonpath='{.items[0].spec.selector.matchLabels}' | jq -r 'to_entries|map("\(.key)=\(.value)")|join(",")')" -o jsonpath='{range .items[*]}{.metadata.labels.openchoreo\.dev/component-uid}{"\n"}{end}' | sort -u | head -n1)
   POD_NAMESPACE=$(kubectl get deploy -A -l openchoreo.dev/component=react-starter -o jsonpath='{.items[0].metadata.namespace}')
   kubectl logs -n $POD_NAMESPACE -l openchoreo.dev/component-uid=$POD_UUID --tail=50
   ```

6. **Verify the web application URL:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=react-starter -o jsonpath='{.items[0].spec.hostnames[0]}'
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-image/react-starter-web-app/react-starter.yaml
```



File: samples/from-source/projects/url-shortener/README.md
---
# Snip URL Shortener on OpenChoreo

A sample application that demonstrates OpenChoreo's **tracing**, **alerting**, and **RCA agent** capabilities using a multi-service URL shortener.

## Prerequisites

- An OpenChoreo cluster with the control plane and observability plane installed (and RCA agent setup for RCA)
- `kubectl` access to the cluster

## Deploy

```bash
kubectl apply -f samples/from-source/projects/url-shortener/project.yaml
kubectl apply -f samples/from-source/projects/url-shortener/components/
```

This deploys five components (snip-postgres, snip-redis, snip-api-service, snip-analytics-service, snip-frontend). Distributed tracing works out of the box once deployed.

For alerting and the RCA agent, follow the setup below.

## Alerting & RCA Agent

A log-based alert rule on the frontend triggers when `status=500` appears more than 5 times within 1 minute.

### Setup

The alert trait is already attached to the snip-frontend component. Set up the notification channel and enable the alert:

```bash
kubectl apply -f samples/from-source/projects/url-shortener/alerting-demo/alert-notification-channels.yaml
kubectl apply -f samples/from-source/projects/url-shortener/alerting-demo/enable-alert.yaml
```

### Trigger the Alert

`failure-scenario.yaml` misconfigures the api-service's `POSTGRES_DSN` to point to a non-existent host. The api-service starts but every DB query fails, returning 500s. This breaches the alert threshold. The RCA agent then traces from the frontend alert to api-service 500s to Postgres connection errors to the misconfigured DSN.

Start generating traffic (auto-detects the frontend URL from the ReleaseBinding):

```bash
chmod +x samples/from-source/projects/url-shortener/alerting-demo/trigger-alerts.sh
./samples/from-source/projects/url-shortener/alerting-demo/trigger-alerts.sh
```

Inject the misconfigured Postgres DSN:

```bash
kubectl apply -f samples/from-source/projects/url-shortener/alerting-demo/failure-scenario.yaml
```

After the alert fires, revert by applying the fix from the UI if suggested, or manually via:

```bash
kubectl patch releasebinding snip-api-service-development --type=json -p '[{"op":"remove","path":"/spec/workloadOverrides"}]'
```

## Cleanup

```bash
kubectl delete -f samples/from-source/projects/url-shortener/project.yaml
```



File: samples/component-types/component-web-app/README.md
---
# Web Application Component Sample

This sample demonstrates how to deploy a web application component in OpenChoreo using the component types.

## Overview

This sample includes the following OpenChoreo Custom Resources:

### ComponentType (`web-service`)

Defines a reusable component type template for web services. It:

- Specifies the workload type as `deployment`
- Defines a schema with configurable parameters (replicas, port, resources)
- Declares environment-specific overrides for resource limits
- Templates the underlying Kubernetes resources (Deployment, Service, HTTPRoute)
- Uses CEL expressions to dynamically populate values from component metadata and parameters

This allows you to create multiple web service components using the same template with different configurations.

### Component (`demo-app-web-service`)

Defines the actual web application component using the `web-service` type. It:

- References the `deployment/web-service` component type
- Specifies configuration parameters:
  - 2 replicas
  - Port 80
  - CPU and memory resource requests/limits
- Belongs to the `default` project

### Workload (`demo-app-web-service-workload`)

Specifies the container image and configuration for the component:

- Links to the `demo-app-web-service` component
- Defines the container image (`choreoanonymouspullable.azurecr.io/react-spa:v0.9`)
- Can specify multiple containers if needed

### ReleaseBinding (`demo-app-web-service-development`)

Represents a deployment instance of the component to a specific environment:

- Links to the `demo-app-web-service` component
- Targets the `development` environment
- Provides environment-specific overrides (reduced resource limits for dev)

## How It Works

1. **ComponentType** acts as a template/blueprint
2. **Component** uses that template and provides base configuration
3. **Workload** specifies what container(s) to run
4. **ReleaseBinding** specifies the actual deployment of the component in a specific environment

The controller reads these resources and generates the Kubernetes resources (Deployment, Service, HTTPRoute) based on the templates and parameters.

## Apply resources

Apply the sample:

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-web-app/webapp-component.yaml
```

## Check the ReleaseBinding status

```bash
kubectl get releasebinding demo-app-web-service-development -o yaml | grep -A 50 "^status:"
```

# Test the Web App by opening it via a web browser

Open your web browser and go to http://http-demo-app-web--development-default-ee0f64b2.openchoreoapis.localhost:19080/.

> **Note:** The hostname is generated by `oc_dns_label` using the endpoint name, component name, environment, and namespace, with a deterministic hash suffix. To find the exact hostname for your deployment, run:
> ```bash
> kubectl get httproute -A -l openchoreo.dev/component=demo-app-web-service -o jsonpath='{.items[0].spec.hostnames[0]}'
> ```

## Cleanup

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-web-app/webapp-component.yaml
```

## Troubleshooting

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding demo-app-web-service-development -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding demo-app-web-service-development -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=demo-app-web-service -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=demo-app-web-service
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=demo-app-web-service -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=demo-app-web-service --tail=50
   ```

6. **Verify service endpoints:**
   ```bash
   kubectl get service -A -l openchoreo.dev/component=demo-app-web-service
   ```



File: samples/component-types/component-with-embedded-traits/README.md
---
# Component with Embedded Traits Example

This example demonstrates PE-defined embedded traits in ComponentTypes, where Platform Engineers pre-configure trait instances that are automatically applied to all Components of that type.

## Overview

This example shows:

- Embedded traits with CEL expression bindings
- Extending the default service component type structure with embedded traits
- Wired vs locked parameter bindings
- Allowed traits restriction for developers
- Environment-specific trait overrides

## Components

The example includes a `component-with-embedded-traits.yaml` file containing all resources for easy deployment.

### Trait (`horizontal-pod-autoscaler`)

Defines a HorizontalPodAutoscaler trait that:

- **Creates**: A HorizontalPodAutoscaler (when enabled)
- Uses `includeWhen` for conditional creation
- Supports environment-specific replica bound overrides

Key features:

- `enabled` parameter controls HPA creation
- `minReplicas`, `maxReplicas` for controlling autoscaling bounds
- `targetCPUUtilizationPercentage` for CPU-based scaling threshold
- Environment overrides via `environmentConfigs.minReplicas` and `environmentConfigs.maxReplicas`

### Trait (`persistent-volume`)

Defines a persistent volume trait that:

- **Creates**: A PersistentVolumeClaim
- **Patches**: Adds volume and volumeMount to the Deployment

### ComponentType (`service-with-autoscaling`)

Defines a component type that extends the default service structure with an embedded HPA trait:

- **Based on**: Default `deployment/service` component type structure
- **Embedded trait**: `horizontal-pod-autoscaler` with instance name `autoscaler`
- **Wired parameter bindings**: CEL expressions like `${parameters.autoscaling.enabled}`
- **Allowed traits**:`observability-alert-rule`, and `persistent-volume` can be added by developers
- **Allowed workflows**: `google-cloud-buildpacks`, `ballerina-buildpack`, and `docker`

Key features:

- Uses the same resource structure as the default service component type
- Exposes autoscaling config through ComponentType schema
- Developers configure HPA without knowing about the underlying trait
- **Embedded trait parameters demonstrate three patterns:**
  - **Locked**: `targetCPUUtilizationPercentage: 75` - PE enforces a fixed value (platform policy)
  - **Developer-configurable**: `minReplicas`, `maxReplicas` - Developers set scaling bounds via parameters
  - **Environment-tunable**: Platform teams can override replica bounds per environment via componentTypeEnvironmentConfigs

### Component (`demo-app-with-embedded-traits`)

Defines a component that:

- Uses the `service-with-autoscaling` component type
- Enables and configures autoscaling via ComponentType parameters (2-10 replicas)
- Note: CPU threshold is locked by PE at 75%, not configurable by developers
- Adds a `persistent-volume` trait (from allowed list)

### Workload

Represents the build output with:

- Container image: `ghcr.io/openchoreo/samples/greeter-service:latest`
- Configured to run on port 9090

### ReleaseBinding

Defines deployment settings for the `development` environment:

- Sets replicas to 3 for adequate redundancy
- Reduces resource requests/limits for cost savings via `componentTypeEnvironmentConfigs.resources`
- Overrides autoscaling replica bounds to 1-5 via `componentTypeEnvironmentConfigs.autoscaling` (environment-tunable)
- Note: `targetCPUUtilizationPercentage` is locked by PE at 75% and cannot be changed per environment
- Overrides PVC size to 10Mi via `traitEnvironmentConfigs.data-storage`

## How It Works

1. **PE extends default service type** by copying its structure and adding embedded HPA trait
2. **PE locks CPU threshold** at 75% while exposing replica bounds to developers
3. **Developer creates Component** and configures autoscaling replica bounds (2-10) via ComponentType parameters
4. **Binding resolution**: CEL expressions like `${parameters.autoscaling.enabled}` are resolved against the component context
5. **Trait renders**: The HPA trait receives resolved values (75% CPU threshold locked, replica bounds from component)
6. **Environment overrides**: ReleaseBinding can override replica bounds per environment (e.g., 1-5 for dev)

## Deploy the sample

Apply the sample:

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-with-embedded-traits/component-with-embedded-traits.yaml
```

## Check the ReleaseBinding status

```bash
kubectl get releasebinding demo-app-with-embedded-traits-development -o yaml | grep -A 50 "^status:"
```

## Test the Service

Once deployed, test the greeter service. The service is exposed at the path `/{component-name}-{endpoint-name}`. For this sample, the component name is `demo-app-with-embedded-traits` and the endpoint name is `http`.

```bash
curl http://development-default.openchoreoapis.localhost:19080/demo-app-with-embedded-traits-http/greeter/greet
```

Output:
```text
Hello, Stranger!
```

With a name parameter:
```bash
curl "http://development-default.openchoreoapis.localhost:19080/demo-app-with-embedded-traits-http/greeter/greet?name=Alice"
```

Output:
```text
Hello, Alice!
```

## Key Features Demonstrated

### 1. Extending Default Component Types

- ComponentType uses the same structure as the default `deployment/service` type
- Adds embedded HPA trait for automatic scaling
- Maintains compatibility with standard service features (endpoints, configs, secrets)

### 2. Embedded Traits

- PE pre-configures traits in ComponentType
- Traits are automatically applied to all Components
- Developers configure through simple ComponentType parameters

### 3. CEL Bindings and Parameter Patterns

- **Locked**: `targetCPUUtilizationPercentage: 75` - Concrete values controlled by PE (platform policy)
- **Wired**: `${parameters.autoscaling.minReplicas}` - References ComponentType schema (developer-configurable)
- **Environment-tunable**: `${environmentConfigs.autoscaling.maxReplicas}` - Per-environment overrides

### 4. Allowed Traits

- `allowedTraits` restricts which traits developers can add
- Embedded traits are always applied (not in allowedTraits list)

### 5. Environment Overrides

- **Environment-tunable overrides**: Use `componentTypeEnvironmentConfigs` to override replica bounds per environment (e.g., `autoscaling.minReplicas`, `autoscaling.maxReplicas`)
- **Locked parameters**: Set by PE in embedded trait, cannot be changed per environment (e.g., `targetCPUUtilizationPercentage: 75`)
- **Developer trait overrides**: Use `traitEnvironmentConfigs[instanceName]` to override developer-added traits (e.g., `data-storage.size`)

## Cleanup

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/refs/heads/main/samples/component-types/component-with-embedded-traits/component-with-embedded-traits.yaml
```

## Troubleshooting

If the application is not accessible or resources are not created:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding demo-app-with-embedded-traits-development -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding demo-app-with-embedded-traits-development -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=demo-app-with-embedded-traits -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=demo-app-with-embedded-traits
   ```

5. **Check HorizontalPodAutoscaler status (embedded trait):**
   ```bash
   kubectl get hpa -A -l openchoreo.dev/component=demo-app-with-embedded-traits
   ```

6. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=demo-app-with-embedded-traits -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=demo-app-with-embedded-traits --tail=50
   ```

7. **Verify service endpoints:**
   ```bash
   kubectl get service -A -l openchoreo.dev/component=demo-app-with-embedded-traits
   ```

8. **Verify PersistentVolumeClaim (developer-added trait):**
   ```bash
   kubectl get pvc -A -l openchoreo.dev/component=demo-app-with-embedded-traits
   ```



File: samples/from-source/services/ballerina-buildpack-patient-management/README.md
---
# Patient Management Service (Mediflow)

## Overview

The **MediFlow** service provides functionalities to manage patient data, including:

- Adding a new patient
- Retrieving patient details by name
- Listing all patients

The service exposes several REST endpoints for performing these operations.

### Health Check

**Endpoint:** `/health`  
**Functionality:** Ensures the service is running.

### Add a new patient

**Endpoint:** `/patients`  
**Method:** `POST`  
**Functionality:** Adds a new patient by sending a JSON payload.

### Retrieve a patient by name

**Endpoint:** `/patients/{name}`  
**Method:** `GET`  
**Functionality:** Retrieves patient details by their name.

### List all patients

**Endpoint:** `/patients`  
**Method:** `GET`  
**Functionality:** Retrieves all patients.

The source code is available at:
https://github.com/openchoreo/sample-workloads/tree/main/service-ballerina-patient-management


## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo. It will also trigger a workflow by creating a workflow resource.

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/ballerina-buildpack-patient-management/patient-management-service.yaml
```

> [!NOTE]
> The workflow will take around 5-8 minutes depending on the network speed and system resources.

## Step 2: Monitor the Workflow

After deploying, monitor the workflow progress:

```bash
# Check WorkflowRun status
kubectl get workflowrun patient-management-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .

# Watch workflow pods (in workflows-default namespace)
kubectl get pods -n workflows-default | grep patient-management

# View workflow logs (replace <pod-name> with actual pod name)
kubectl logs -n workflows-default <pod-name> -f
```

Wait for the WorkflowRun to complete successfully. You should see:
- `WorkflowCompleted: True`
- `WorkflowSucceeded: True`
- `WorkloadUpdated: True`

## Step 3: Verify Deployment

After the workflow completes, verify the deployment is ready:

```bash
# Check ReleaseBinding status
kubectl get releasebinding patient-management-service-development -n default -o jsonpath='{.status.conditions}' | jq .

# Verify deployment is ready
kubectl get deployment -A -l openchoreo.dev/component=patient-management-service
```

## Step 4: Test the Application

First, get the service URL from the HTTPRoute:

```bash
# Get the hostname and path prefix from the HTTPRoute
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=patient-management-service -o jsonpath='{.items[0].spec.hostnames[0]}')
PATH_PREFIX=$(kubectl get httproute -A -l openchoreo.dev/component=patient-management-service -o jsonpath='{.items[0].spec.rules[0].matches[0].path.value}')
```

### Health check
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/mediflow/health"
```

Example with direct URL (base path is `/{component-name}-{endpoint-name}`). For this sample, the component name is `patient-management-service`:

```bash
curl http://development-default.openchoreoapis.localhost:19080/patient-management-service-patient-management-api/mediflow/health
```

### Add a new patient
```bash
curl -X POST "http://${HOSTNAME}:19080${PATH_PREFIX}/mediflow/patients" \
-H "Content-Type: application/json" \
-d '{
"name": "Alice",
"age": 30,
"condition": "Healthy"
}'
```

### Retrieve a patient by name
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/mediflow/patients/Alice"
```

### List all patients
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/mediflow/patients"
```

## Troubleshooting

### Workflow Issues

If the workflow fails or takes too long:

1. **Check WorkflowRun status and conditions:**
   ```bash
   kubectl get workflowrun patient-management-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .
   ```

2. **Check workflow pod status:**
   ```bash
   kubectl get pods -n workflows-default | grep patient-management
   ```

3. **View workflow pod logs for errors:**
   ```bash
   # Get the pod name
   POD_NAME=$(kubectl get pods -n workflows-default -l component-workflows.argoproj.io/workflow=patient-management-service-build-01 --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

   # View logs
   kubectl logs -n workflows-default $POD_NAME
   ```

4. **Check if Workload was created after workflow:**
   ```bash
   kubectl get workload -n default | grep patient-management
   ```

### Deployment Issues

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding patient-management-service-development -n default -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding patient-management-service-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=patient-management-service -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=patient-management-service
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=patient-management-service -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=patient-management-service --tail=50
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/ballerina-buildpack-patient-management/patient-management-service.yaml
```



File: samples/from-source/services/go-docker-greeter/README.md
---
# Greeting Service

## Overview

This sample demonstrates how to deploy a simple Go REST service in Choreo from the source code.
The service exposes one REST endpoint.

Exposed REST endpoints:

### Greet a user

**Endpoint:** `/greeter/greet`
**Method:** `GET`
**Functionality:** Sends a greeting to the user.

The source code is available at:
https://github.com/openchoreo/sample-workloads/tree/main/service-go-greeter

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo. It will also trigger a workflow by creating a workflow resource.

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/go-docker-greeter/greeting-service.yaml
```

> [!NOTE]
> The Docker workflow will take around 3-5 minutes depending on the network speed and system resources.

## Step 2: Monitor the Workflow

After deploying, monitor the workflow progress:

```bash
# Check WorkflowRun status
kubectl get workflowrun greeting-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .

# Watch workflow pods (in workflows-default namespace)
kubectl get pods -n workflows-default | grep greeting-service

# View workflow logs (replace <pod-name> with actual pod name)
kubectl logs -n workflows-default <pod-name> -f
```

Wait for the WorkflowRun to complete successfully. You should see:
- `WorkflowCompleted: True`
- `WorkflowSucceeded: True`
- `WorkloadUpdated: True`

## Step 3: Verify Deployment

After the workflow completes, verify the deployment is ready:

```bash
# Check ReleaseBinding status
kubectl get releasebinding greeting-service-development -n default -o jsonpath='{.status.conditions}' | jq .

# Verify deployment is ready
kubectl get deployment -A -l openchoreo.dev/component=greeting-service
```

## Step 4: Test the Application

First, get the service URL from the HTTPRoute:

```bash
# Get the hostname and path prefix from the HTTPRoute
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=greeting-service -o jsonpath='{.items[0].spec.hostnames[0]}')
PATH_PREFIX=$(kubectl get httproute -A -l openchoreo.dev/component=greeting-service -o jsonpath='{.items[0].spec.rules[0].matches[0].path.value}')
```

### Basic Greet
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/greeter/greet"
```

### Greet with name
```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/greeter/greet?name=Alice"
```

### Example with direct URL (base path is /{component-name})
The service is exposed at the base path `/{component-name}-{endpoint-name}`. For this sample, the component name is `greeting-service`.

```bash
curl http://development-default.openchoreoapis.localhost:19080//greeting-service-greeter-api/greeter/greet
```

## Troubleshooting

### Workflow Issues

If the workflow fails or takes too long:

1. **Check WorkflowRun status and conditions:**
   ```bash
   kubectl get workflowrun greeting-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .
   ```

2. **Check workflow pod status:**
   ```bash
   kubectl get pods -n workflows-default | grep greeting-service
   ```

3. **View workflow pod logs for errors:**
   ```bash
   # Get the pod name
   POD_NAME=$(kubectl get pods -n workflows-default -l component-workflows.argoproj.io/workflow=greeting-service-build-01 --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

   # View logs
   kubectl logs -n workflows-default $POD_NAME
   ```

4. **Check if Workload was created after workflow:**
   ```bash
   kubectl get workload -n default | grep greeting-service
   ```

### Deployment Issues

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding greeting-service-development -n default -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding greeting-service-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=greeting-service -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=greeting-service
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=greeting-service -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=greeting-service --tail=50
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/go-docker-greeter/greeting-service.yaml
```



File: samples/from-source/services/go-google-buildpack-reading-list/README.md
---
# Reading List Service
The Reading List Service allows you to manage a collection of books, including:
- Adding a new book
- Retrieving book details by ID
- Updating book information
- Deleting a book
- Listing all books

The service exposes several REST endpoints for performing these operations.

### Add a new book
**Endpoint:** `/reading-list/books`  
**Method:** `POST`  
**Functionality:** Adds a new book to the reading list by sending a JSON payload.

### Retrieve a book by ID
**Endpoint:** `/reading-list/books/{id}`  
**Method:** `GET`  
**Functionality:** Retrieves book details by their ID.

### Update a book
**Endpoint:** `/reading-list/books/{id}`  
**Method:** `PUT`  
**Functionality:** Updates book information by sending a JSON payload.

### Delete a book
**Endpoint:** `/reading-list/books/{id}`  
**Method:** `DELETE`  
**Functionality:** Deletes a book from the reading list.

### List all books
**Endpoint:** `/reading-list/books`  
**Method:** `GET`  
**Functionality:** Retrieves all books from the reading list.

The source code is available at:
https://github.com/openchoreo/sample-workloads/tree/main/service-go-reading-list

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo. It will also trigger a workflow by creating a workflow resource.

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/go-google-buildpack-reading-list/reading-list-service.yaml
```

> [!NOTE]
> The Google Cloud Buildpack workflow will take around 5-8 minutes depending on the network speed and system resources.

## Step 2: Monitor the Workflow

After deploying, monitor the workflow progress:

```bash
# Check WorkflowRun status
kubectl get workflowrun reading-list-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .

# Watch workflow pods (in workflows-default namespace)
kubectl get pods -n workflows-default | grep reading-list

# View workflow logs (replace <pod-name> with actual pod name)
kubectl logs -n workflows-default <pod-name> -f
```

Wait for the WorkflowRun to complete successfully. You should see:
- `WorkflowCompleted: True`
- `WorkflowSucceeded: True`
- `WorkloadUpdated: True`

## Step 3: Verify Deployment

After the workflow completes, verify the deployment is ready:

```bash
# Check ReleaseBinding status
kubectl get releasebinding reading-list-service-development -n default -o jsonpath='{.status.conditions}' | jq .

# Verify deployment is ready
kubectl get deployment -A -l openchoreo.dev/component=reading-list-service
```

## Step 4: Test the Application

First, get the service URL from the HTTPRoute:

```bash
# Get the hostname and path prefix from the HTTPRoute
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=reading-list-service -o jsonpath='{.items[0].spec.hostnames[0]}')
PATH_PREFIX=$(kubectl get httproute -A -l openchoreo.dev/component=reading-list-service -o jsonpath='{.items[0].spec.rules[0].matches[0].path.value}')
```

### Add a new book

```bash
curl -X POST "http://${HOSTNAME}:19080${PATH_PREFIX}/api/v1/reading-list/books" \
-H "Content-Type: application/json" \
-d '{
"id": "12",
"title": "The Catcher in the Rye",
"author": "J.D. Salinger",
"status": "reading"
}'
```

### Retrieve the book by ID

```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/api/v1/reading-list/books/12"
```

### Update a book

```bash
curl -X PUT "http://${HOSTNAME}:19080${PATH_PREFIX}/api/v1/reading-list/books/12" \
-H "Content-Type: application/json" \
-d '{
"title": "The Catcher in the Rye",
"author": "J.D. Salinger",
"status": "read"
}'
```

### Delete a book by ID

```bash
curl -X DELETE "http://${HOSTNAME}:19080${PATH_PREFIX}/api/v1/reading-list/books/12"
```

### List all books

```bash
curl "http://${HOSTNAME}:19080${PATH_PREFIX}/api/v1/reading-list/books"
```

## Troubleshooting

### Workflow Issues

If the workflow fails or takes too long:

1. **Check WorkflowRun status and conditions:**
   ```bash
   kubectl get workflowrun reading-list-service-build-01 -n default -o jsonpath='{.status.conditions}' | jq .
   ```

2. **Check workflow pod status:**
   ```bash
   kubectl get pods -n workflows-default | grep reading-list
   ```

3. **View workflow pod logs for errors:**
   ```bash
   # Get the pod name
   POD_NAME=$(kubectl get pods -n workflows-default -l component-workflows.argoproj.io/workflow=reading-list-service-build-01 --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

   # View logs
   kubectl logs -n workflows-default $POD_NAME
   ```

4. **Check if Workload was created after workflow:**
   ```bash
   kubectl get workload -n default | grep reading-list
   ```

### Deployment Issues

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding reading-list-service-development -n default -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding reading-list-service-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=reading-list-service -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=reading-list-service
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=reading-list-service -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=reading-list-service --tail=50
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/services/go-google-buildpack-reading-list/reading-list-service.yaml
```



File: samples/from-source/web-apps/react-starter/README.md
---
# React Starter Web Application

## Overview

This sample demonstrates how to deploy a React web application in OpenChoreo from source code. The application is built using Node.js 20 and served using nginx.

The source code is available at:
https://github.com/openchoreo/sample-workloads/tree/main/webapp-react-nginx

## Step 1: Deploy the Application

The following command will create the relevant resources in OpenChoreo:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/web-apps/react-starter/react-web-app.yaml
```

> [!NOTE]
> The React workflow will take around 4-6 minutes depending on the network speed and Node.js dependency installation.

## Step 2: Monitor the Workflow

After deploying, monitor the workflow progress:

```bash
# Check WorkflowRun status
kubectl get workflowrun react-starter-build-01 -n default -o jsonpath='{.status.conditions}' | jq .

# Watch build pods (in workflows-default namespace)
kubectl get pods -n workflows-default | grep react-starter

# View build logs (replace <pod-name> with actual pod name)
kubectl logs -n workflows-default <pod-name> -f
```

Wait for the WorkflowRun to complete successfully. You should see:
- `WorkflowCompleted: True`
- `WorkflowSucceeded: True`
- `WorkloadUpdated: True`

## Step 3: Verify Deployment

After the workflow completes, verify the deployment is ready:

```bash
# Check ReleaseBinding status
kubectl get releasebinding react-starter-from-source-development -n default -o jsonpath='{.status.conditions}' | jq .

# Verify deployment is ready
kubectl get deployment -A -l openchoreo.dev/component=react-starter-from-source
```

## Step 4: Access the Application

Once the application is deployed, you can access the React application at:


http://http-react-starter-development-default-61697d54.openchoreoapis.localhost:19080


You can also dynamically get the URL using:

```bash
HOSTNAME=$(kubectl get httproute -A -l openchoreo.dev/component=react-starter-from-source -o jsonpath='{.items[0].spec.hostnames[0]}')
echo "Access the application at: http://${HOSTNAME}:19080"
```

## Troubleshooting

### Workflow Issues

If the workflow fails or takes too long:

1. **Check WorkflowRun status and conditions:**
   ```bash
   kubectl get workflowrun react-starter-build-01 -n default -o jsonpath='{.status.conditions}' | jq .
   ```

2. **Check workflow pod status:**
   ```bash
   kubectl get pods -n workflows-default | grep react-starter
   ```

3. **View workflow pod logs for errors:**
   ```bash
   # Get the pod name
   POD_NAME=$(kubectl get pods -n workflows-default -l component-workflows.argoproj.io/workflow=react-starter-build-01 --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

   # View logs
   kubectl logs -n workflows-default $POD_NAME
   ```

4. **Check if Workload was created after workflow:**
   ```bash
   kubectl get workload -n default | grep react-starter
   ```

### Deployment Issues

If the application is not accessible:

1. **Check ReleaseBinding status:**
   ```bash
   kubectl get releasebinding react-starter-from-source-development -n default -o yaml
   ```

2. **Check ReleaseBinding conditions:**
   ```bash
   kubectl get releasebinding react-starter-from-source-development -n default -o jsonpath='{.status.conditions}' | jq .
   ```

3. **Verify HTTPRoute is configured:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=react-starter-from-source -o yaml
   ```

4. **Check deployment status:**
   ```bash
   kubectl get deployment -A -l openchoreo.dev/component=react-starter-from-source
   ```

5. **Check pod logs:**
   ```bash
   kubectl logs -n $(kubectl get pods -A -l openchoreo.dev/component=react-starter-from-source -o jsonpath='{.items[0].metadata.namespace}') -l openchoreo.dev/component=react-starter-from-source --tail=50
   ```

6. **Verify the web application URL:**
   ```bash
   kubectl get httproute -A -l openchoreo.dev/component=react-starter-from-source -o jsonpath='{.items[0].spec.hostnames[0]}'
   ```

## Clean Up

Remove all resources:

```bash
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/from-source/web-apps/react-starter/react-web-app.yaml
```



File: samples/gcp-microservices-demo/README.md
---
# Google Microservices Demo Sample

This sample demonstrates how to deploy Google's microservices demo application using OpenChoreo.

## Overview

This sample demonstrates a complete microservices architecture deployment using the Google Cloud Platform's microservices demo application. It showcases multiple services working together using OpenChoreo.

## Pre-requisites

- Kubernetes cluster with OpenChoreo installed
- The `kubectl` CLI tool installed
- Docker runtime capable of running AMD64 images (see note below)

> [!NOTE]
> #### Architecture Compatibility
> This sample uses official Google Container Registry images built for AMD64 architecture. 
> If you're on Apple Silicon (M1/M2) or ARM-based systems, your container runtime may need 
> to emulate AMD64. To verify your setup can run AMD64 images:
> ```bash
> docker run --rm --platform linux/amd64 hello-world
> ```
> If this command fails, you may need to enable emulation support in your container runtime.

## File Structure

```
gcp-microservices-demo/
├── gcp-microservice-demo-project.yaml    # Project definition
├── components/                           # Component definitions
│   ├── ad-component.yaml                 # Ad service component
│   ├── cart-component.yaml               # Cart service component
│   ├── checkout-component.yaml           # Checkout service component
│   ├── currency-component.yaml           # Currency service component
│   ├── email-component.yaml              # Email service component
│   ├── frontend-component.yaml           # Frontend web application
│   ├── payment-component.yaml            # Payment service component
│   ├── productcatalog-component.yaml     # Product catalog service component
│   ├── recommendation-component.yaml     # Recommendation service component
│   ├── redis-component.yaml              # Redis cache component
│   └── shipping-component.yaml           # Shipping service component
└── README.md                             # This guide
```

## Step 1: Create the Project

First, create the project that will contain all the microservices:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/gcp-microservice-demo-project.yaml
```

## Step 2: Deploy the Components

Deploy all the microservices components:

```bash
kubectl apply \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/ad-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/cart-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/checkout-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/currency-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/email-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/frontend-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/payment-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/productcatalog-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/recommendation-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/redis-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/shipping-component.yaml
```

This will deploy all the microservices using official Google Container Registry images.

## (Optional) Enable Distributed Tracing

Most services in this demo are pre-instrumented with OpenTelemetry. You can enable trace collection by pointing them to OpenChoreo's OpenTelemetry Collector.

> [!NOTE]
> #### Per-service tracing support
> | Service | Language | Tracing support |
> |---|---|---|
> | frontend, checkout, productcatalog | Go | Full — via `COLLECTOR_SERVICE_ADDR` + `ENABLE_TRACING=1` |
> | currency, payment | Node.js | Full — via `COLLECTOR_SERVICE_ADDR` + `ENABLE_TRACING=1` |
> | email, recommendation | Python | Full — via `COLLECTOR_SERVICE_ADDR` + `ENABLE_TRACING=1` |
> | shipping | Go | Not implemented (TODO in source) |
> | ad | Java | Not implemented (TODO in source) |
> | cart | .NET | Not implemented |

Patch the workloads to add the collector address:

```bash
COLLECTOR_ADDR="opentelemetry-collector.openchoreo-observability-plane.svc.cluster.local:4317"
# frontend, checkout, productcatalog, currency, payment, email, recommendation
for svc in checkout currency email frontend payment productcatalog recommendation; do
  kubectl patch workload "$svc" -n default --type='json' -p='[
    {"op": "add", "path": "/spec/container/env/-", "value": {"key": "COLLECTOR_SERVICE_ADDR", "value": "'"$COLLECTOR_ADDR"'"}},
    {"op": "add", "path": "/spec/container/env/-", "value": {"key": "ENABLE_TRACING", "value": "1"}}
  ]'
done
```

> [!NOTE]
> `shipping` (Go), `ad` (Java), and `cart` (C#/.NET) do not have OpenTelemetry tracing implemented in the current upstream source and will not emit traces regardless of configuration.

For more details on traces, see the [Observability & Alerting guide](https://openchoreo.dev/docs/platform-engineer-guide/observability-alerting/#traces).

## Step 3: Test the Application

Access the frontend application in your browser:

```
http://http-frontend-development-default-4cc7110c.openchoreoapis.localhost:19080
```

> [!TIP]
> #### Verification
>
> You should see the Google Cloud Platform microservices demo store frontend with:
> - Product catalog
> - Shopping cart functionality
> - Checkout process

> [!NOTE]
> #### Startup Time
> All services may take 5-10 minutes to become fully operational. The URL will return errors or be unreachable until everything is ready.

## Clean Up

Remove all resources:

```bash
# Remove components
kubectl delete \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/ad-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/cart-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/checkout-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/currency-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/email-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/frontend-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/payment-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/productcatalog-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/recommendation-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/redis-component.yaml \
-f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/components/shipping-component.yaml

# Remove project
kubectl delete -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/gcp-microservices-demo/gcp-microservice-demo-project.yaml
```



File: samples/mcp/README.md
---
# OpenChoreo MCP Server - AI Assistant Examples

This directory contains practical guides for using the OpenChoreo MCP (Model Context Protocol) server with AI assistants like Claude Code, Cursor, VS Code, and Claude Desktop.

## Prerequisites

Before you begin, ensure you have completed the following prerequisites:

### 1. Running OpenChoreo Instance

You need a running OpenChoreo instance. If you haven't set one up yet:

- Complete the [Quick Start Guide](https://openchoreo.dev/docs/getting-started/quick-start-guide/)
- Or follow the [Installation Guide](https://openchoreo.dev/docs/getting-started/try-it-out/on-k3d-locally/) for your preferred setup method

### 2. Configure MCP Server

The OpenChoreo MCP server must be configured and accessible. See the [Configuration Guide](https://openchoreo.dev/docs/ai/mcp-servers) for detailed instructions to obtain:

- MCP server endpoint
- An access token

### 3. AI Assistant Setup

Install an AI Assistant (AI Agent) and configure the OpenChoreo MCP server.
- Transport: `http`
- Authorization header

## Guides

### 1. [Getting Started](./getting-started/)
Learn the basics of connecting your AI assistant to OpenChoreo and performing simple operations like listing namespaces and projects.

**Prerequisites:** All prerequisites above must be completed.

**Time:** 2 minutes

### 2. [Service Deployment](./service-deployment/)
Deploy a complete service from source code to production using the OpenChoreo MCP server. Choose from:

- **[Step-by-Step Guide](./service-deployment/step-by-step/)** - Guided walkthrough with explicit prompts
- **[Developer Chat](./service-deployment/developer-chat/)** - Natural conversation-based deployment

**Prerequisites:** All prerequisites above, plus:
- At least two environments configured (development and production)
- Component workflows configured (Docker or Buildpacks)

**Time:** 15-20 minutes

### 3. [Log Analysis & Debugging](./log-analysis/)
Debug a cascading failure in the GCP Microservices Demo (Online Boutique) using logs, traces, and workload inspection. You'll intentionally break the product catalog service, then use AI-assisted observability to diagnose and fix the issue.

**Prerequisites:** All prerequisites above, plus:
- [GCP Microservices Demo](../gcp-microservices-demo/) deployed and running
- Observability plane configured and running
- Both Control Plane and Observability Plane MCP servers configured

**Time:** ~10 minutes

### 4. [Build Failure Diagnosis](./build-failures/)
Debug a Docker build failure in the Go Greeter service. You'll trigger a build with a misconfigured Dockerfile path, then use AI-assisted workflow inspection and log analysis to diagnose and fix the issue.

**Prerequisites:** All prerequisites above, plus:
- [Go Docker Greeter](../from-source/services/go-docker-greeter/) sample deployed with a successful initial build
- Workflow plane installed and running
- Both Control Plane and Observability Plane MCP servers configured

**Time:** ~10 minutes

### 5. [Resource Optimization](./resource-optimization/)
Detect and fix over-provisioned workloads in the GCP Microservices Demo. You'll intentionally allocate excessive CPU and memory, then use AI-assisted analysis to compare allocation vs actual usage and apply right-sized configurations.

**Prerequisites:** All prerequisites above, plus:
- [GCP Microservices Demo](../gcp-microservices-demo/) deployed and running
- Observability plane configured and running
- Both Control Plane and Observability Plane MCP servers configured

**Time:** ~10 minutes

## Getting Help

- [OpenChoreo Documentation](https://openchoreo.dev/)
- [Slack Community](https://cloud-native.slack.com/archives/C0ABYRG1MND)



File: samples/getting-started/README.md
---
# Getting Started Resources

Default resources for OpenChoreo. Apply these after installing the control plane to set up a working environment with projects, environments, component types, and build workflows.

## Quick Start

Apply all resources with a single command:

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/getting-started/all.yaml
```

Or if you have cloned the repository:

```bash
kubectl apply -f samples/getting-started/all.yaml
```

## Verify Installation

```bash
kubectl get project,environment,deploymentpipeline,componenttype,workflow,trait -n default
```

Expected output:

```
NAME                                   AGE
project.openchoreo.dev/default         10s

NAME                                       AGE
environment.openchoreo.dev/development     10s
environment.openchoreo.dev/production      10s
environment.openchoreo.dev/staging         10s

NAME                                           AGE
deploymentpipeline.openchoreo.dev/default      10s

NAME                                        AGE
componenttype.openchoreo.dev/scheduled-task    10s
componenttype.openchoreo.dev/service           10s
componenttype.openchoreo.dev/web-application   10s
componenttype.openchoreo.dev/worker            10s

NAME                                                   AGE
workflow.openchoreo.dev/ballerina-buildpack             10s
workflow.openchoreo.dev/docker                          10s
workflow.openchoreo.dev/google-cloud-buildpacks         10s
workflow.openchoreo.dev/react                           10s

NAME                                               AGE
trait.openchoreo.dev/observability-alert-rule         10s
```

## What Gets Created

### Project and Pipeline

- **default** project with a deployment pipeline that promotes through development -> staging -> production

### Environments

| Name | DNS Prefix | Production |
|------|------------|------------|
| development | dev | No |
| staging | staging | No |
| production | prod | Yes |

### Component Types

| Name | Workload Type | Build Workflows | Validation |
|------|---------------|-----------------|------------|
| worker | Deployment | docker, google-cloud-buildpacks | No endpoints |
| service | Deployment | docker, google-cloud-buildpacks, ballerina-buildpack | At least 1 endpoint |
| web-application | Deployment | react, docker | HTTP endpoint required |
| scheduled-task | CronJob | docker, google-cloud-buildpacks | - |

### Workflows

| Name | Description |
|------|-------------|
| docker | Build using Dockerfile |
| react | Build React web applications |
| ballerina-buildpack | Build Ballerina applications |
| google-cloud-buildpacks | Build using Google Cloud Buildpacks |

### Traits

| Name | Description |
|------|-------------|
| observability-alert-rule | Define alert rules for log and metric monitoring |

## Individual Files

For applying resources selectively:

```
getting-started/
├── all.yaml                    # Combined manifest
├── project.yaml                # Default project
├── environments.yaml           # Development, staging, production
├── deployment-pipeline.yaml    # Promotion pipeline
├── component-types/
│   ├── worker.yaml
│   ├── service.yaml
│   ├── webapp.yaml
│   └── scheduled-task.yaml
├── ci-workflows/
│   ├── dockerfile-builder.yaml
│   ├── paketo-buildpacks-builder.yaml
│   ├── ballerina-buildpack-builder.yaml
│   └── gcp-buildpacks-builder.yaml
└── component-traits/
    └── alert-rule-trait.yaml
```

## Customization

These are default configurations. You can:

1. Modify the YAML files before applying
2. Apply individual files instead of `all.yaml`
3. Create your own resources using these as templates

See the [Platform Configuration](../platform-config/) samples for more customization examples.



File: samples/mcp/build-failures/README.md
---
# Build Failure Diagnosis with OpenChoreo MCP Server

This guide walks you through a build failure debugging scenario using the OpenChoreo MCP server and AI assistants. You'll trigger a build with a misconfigured Dockerfile path, then use MCP tools to find the failure, inspect the logs, and diagnose the root cause.

## Prerequisites

Before starting this guide, ensure you have completed all [prerequisites](../README.md#prerequisites)

Additionally, you need:

1. **Go Docker Greeter sample deployed** — follow the [Go Docker Greeter](../../from-source/services/go-docker-greeter/) sample to deploy the greeting service from source. Wait for the initial build (`greeting-service-build-01`) to complete successfully before proceeding.
2. **Workflow plane** installed and running — see [Setup Workflow Plane](https://openchoreo.dev/docs/getting-started/try-it-out/on-k3d-locally/#step-6-setup-workflow-plane-optional) guide
3. **Both MCP servers configured** — you need both the Control Plane and Observability Plane MCP servers connected to your AI assistant. See the [Configuration Guide](https://openchoreo.dev/docs/ai/mcp-servers)

## What You'll Learn

- How to use MCP tools to list and inspect workflow runs
- How to retrieve and analyze build logs from a failed workflow
- How to use AI assistants to diagnose build failures and suggest fixes

## Scenario: Misconfigured Dockerfile Path

The Go Docker Greeter service builds from source using the `dockerfile-builder` workflow. We'll trigger a new build with an incorrect Dockerfile path, simulating a common misconfiguration that causes Docker builds to fail.

### Setup context

```
greeting-service (working build: /service-go-greeter/Dockerfile)
                          ↓
  Trigger new build with: /service-go-greeter/Dockerfile.broken  ← does not exist
```

## Step 1: Introduce the Build Failure

Trigger a new workflow run with a wrong Dockerfile path using `kubectl`:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: greeting-service-build-02
  labels:
    openchoreo.dev/project: "default"
    openchoreo.dev/component: "greeting-service"
spec:
  workflow:
    kind: ClusterWorkflow
    name: dockerfile-builder
    parameters:
      repository:
        url: "https://github.com/openchoreo/sample-workloads"
        revision:
          branch: "main"
        appPath: "/service-go-greeter"
      docker:
        context: "/service-go-greeter"
        filePath: "/service-go-greeter/Dockerfile.broken"
EOF
```

Wait a couple of minutes for the build to run and fail.

## Step 2: Discover the Failed Build

Ask the AI assistant to check on recent builds.

```
List the recent workflow runs for the "greeting-service" component in the
"default" namespace and "default" project. Are there any failures?
```

**What agent will do:**
1. Call `list_workflow_runs` (Control Plane MCP) filtered to the greeting-service component
2. Display each workflow run with its status and timestamps
3. Flag the failed run

**Expected:** The assistant should show two workflow runs — `greeting-service-build-01` (succeeded) and `greeting-service-build-02` (failed).

## Step 3: Inspect the Failed Build

Get the details of the failed build to understand which step broke.

```
Show me the details of the "greeting-service-build-02" workflow run.
Which tasks failed?
```

**What agent will do:**
1. Call `get_workflow_run` (Control Plane MCP) with the workflow run name
2. Display the task-level breakdown showing which tasks succeeded and which failed
3. Identify the exact step where the build broke (the Docker build task)

**Expected:** The task breakdown should show that the Docker build step failed while earlier steps like source checkout succeeded.

## Step 4: Retrieve Build Logs

Get the actual error output from the failed build.

```
Get the build logs for the failed "greeting-service-build-02" workflow run.
Show me the error output.
```

**What agent will do:**
1. Call `query_workflow_logs` (Observability MCP) for the failed workflow run
2. Display the relevant log output focusing on the error messages
3. Highlight the key failure lines

**Expected:** The logs should show a Docker build error indicating that the Dockerfile at `/service-go-greeter/Dockerfile.broken` was not found.

## Step 5: Diagnose and Fix

Ask the AI assistant to analyze the failure and recommend a fix.

```
Analyze this build failure. What's the root cause and how should I fix it?
Also look at "greeting-service-build-01" (the previous successful run) to compare
the Dockerfile path it used.
```

**What agent will do:**
1. Compare the failed build's configuration with the successful `greeting-service-build-01`
2. Call `get_workflow_run` (Control Plane MCP) for the successful build to get its parameters
3. Identify that the Dockerfile path was changed from `Dockerfile` to `Dockerfile.broken`
4. Recommend correcting the path back to `/service-go-greeter/Dockerfile`

## Step 6: Trigger a Fixed Build

Apply the fix by triggering a new build with the correct Dockerfile path.

```
Trigger a new workflow run for the greeting-service component using the
dockerfile-builder workflow with the correct Dockerfile path
"/service-go-greeter/Dockerfile". Use the same repository and branch as before.
```

**What agent will do:**
1. Call `create_workflow_run` (Control Plane MCP) with the corrected parameters
2. Confirm the workflow run was created

Then verify:

```
Check the status of the latest greeting-service build. Has it completed successfully?
```

**What agent will do:**
1. Call `list_workflow_runs` or `get_workflow_run` (Control Plane MCP) to check the new build status
2. Confirm it completed successfully

**Expected:** The new build should complete successfully, confirming the fix.

## MCP Tools Used

| Tool | MCP Server | Purpose |
|------|------------|---------|
| `list_workflow_runs` | Control Plane | List builds and find failures |
| `get_workflow_run` | Control Plane | Inspect task-level build details |
| `query_workflow_logs` | Observability | Retrieve build log output |
| `create_workflow_run` | Control Plane | Trigger a new build with corrected config |

## Clean Up

Remove the failed workflow run:

```bash
kubectl delete workflowrun greeting-service-build-02 -n default
```

To remove the entire greeting service, follow the clean up steps in the [Go Docker Greeter](../../from-source/services/go-docker-greeter/) sample.

## Next Steps

- Try the [Log Analysis & Debugging](../log-analysis/) guide to debug cascading failures
- Try the [Resource Optimization](../resource-optimization/) guide to right-size your workloads



File: samples/mcp/configs/README.md
---
# AI Assistant Configuration for OpenChoreo MCP Server

This guide has moved to the OpenChoreo documentation site.

**[Configure MCP Servers with AI Assistants →](https://openchoreo.dev/docs/ai/mcp-servers)**

The docs site covers:
- Browser-based OAuth authentication (recommended)
- Client credentials authentication
- Configuration for Claude Code, Cursor, Gemini CLI, OpenCode CLI, VS Code (GitHub Copilot), and Codex CLI



File: samples/mcp/getting-started/README.md
---
# Getting Started with OpenChoreo MCP Server

This guide walks you through basic operations using the OpenChoreo MCP server. You'll learn how to discover and explore your OpenChoreo resources using AI assistants.

## Prerequisites

Before starting this guide, ensure you have completed all [prerequisites](../README.md#prerequisites)

## What You'll Learn

In this guide, you'll learn:
- How to prompt AI assistants to interact with OpenChoreo using MCP tools
- How to discover and explore your OpenChoreo resources through natural language

## Step 1: Verify MCP Connection

First, verify that your AI assistant can connect to the OpenChoreo MCP server. In your AI assistant, try:

```
Do you have access to the OpenChoreo MCP server? List the available tools.
```

**Expected:** The assistant should confirm MCP access and list available OpenChoreo tools like `list_namespaces`, `list_projects`, `create_component`, etc.

If the connection isn't working, review the [Configuration Guide](https://openchoreo.dev/docs/ai/mcp-servers) to ensure your setup is correct.

## Step 2: Explore OpenChoreo Resources

### Prompt 1: List namespaces

```
List available namespaces in my openchoreo cluster.
```

**What agent will do:**
1. Call `list_namespaces` to list namespaces. Note that this will return only the namespaces which contains the label: `openchoreo.dev/control-plane=true`
2. Display each namespace details including name, display name, and status

### Prompt 2: Get Project Details

```
Show me details of all projects in the "default" namespace
```

**What agent will do:**
1. Call `list_projects` with the namespace name
2. Display project details including description, status, component count, and creation date
3. Offer to show component details for any project

## Next Steps

You've successfully set up and tested the OpenChoreo MCP server! Continue with the [Service Deployment](../service-deployment/) guide to learn how to deploy applications using the MCP server.



File: samples/mcp/log-analysis/README.md
---
# Log Analysis & Debugging with OpenChoreo MCP Server

This guide walks you through a real debugging scenario using the OpenChoreo MCP server and AI assistants. You'll intentionally break a multi-service application, then use logs, traces, and metrics to diagnose and fix the issue.

## Prerequisites

Before starting this guide, ensure you have completed all [prerequisites](../README.md#prerequisites)

Additionally, you need:

1. **GCP Microservices Demo deployed** — follow the [GCP Microservices Demo](../../gcp-microservices-demo/) sample to deploy the Online Boutique application
2. **Observability plane** configured and running — see [Observability & Alerting](https://openchoreo.dev/docs/platform-engineer-guide/observability-alerting/) for setup instructions
3. **Both MCP servers configured** — you need both the Control Plane and Observability Plane MCP servers connected to your AI assistant. See the [Configuration Guide](https://openchoreo.dev/docs/ai/mcp-servers)

## What You'll Learn

- How to use AI assistants to investigate errors across a distributed microservices application
- How to query and analyze component logs filtered by severity and time range
- How to trace requests across service boundaries to find the root cause
- How to correlate logs, traces, and metrics for a complete picture

## Scenario: Breaking the Product Catalog

The GCP Microservices Demo (Online Boutique) has interconnected services. The **product catalog** service is a critical dependency — **checkout**, **recommendation**, and **frontend** all depend on it. We'll scale it down to zero replicas to simulate an outage, then debug the cascading failures.

### Architecture context

```
frontend ──→ productcatalog   ← we'll break this
frontend ──→ checkout ──→ productcatalog
frontend ──→ recommendation ──→ productcatalog
```

## Step 1: Introduce the Failure

Scale the product catalog service to zero replicas by patching its ReleaseBinding. This is the OpenChoreo-native way to change replica count — patching the deployment directly would be overwritten by the controllers.

```bash
kubectl patch releasebinding productcatalog-development -n default \
  --type=merge -p '{"spec": {"componentTypeEnvironmentConfigs": {"replicas": 0}}}'
```

Now visit the frontend in your browser. You should see errors when browsing products or attempting checkout. Let it run for a minute or two so logs and traces accumulate.

## Step 2: Discover the Problem Through Logs

Start your debugging session by asking the AI assistant to check for errors.

```
Are there any errors in the GCP microservices demo application? Check the logs
for components in the "default" namespace, "gcp-microservice-demo" project,
"development" environment. Look at the last 15 minutes.
```

**What agent will do:**
1. Call `list_components` (Control Plane MCP) to discover all components in the project
2. Call `query_component_logs` (Observability MCP) for each component, filtering by error severity and the last 15 minutes
3. Report which components are logging errors and summarize the error messages

**Expected:** The assistant should report errors in **frontend**, **checkout**, and **recommendation** — all complaining about failed connections to the product catalog service.

## Step 3: Trace a Failed Request

Pick a failing request and trace it across service boundaries.

```
Find traces for failed requests in the frontend component over the last 15 minutes.
Show me the spans for one of the failed traces so I can see where the request broke.
```

**What agent will do:**
1. Call `query_traces` (Observability MCP) filtered to the frontend component and recent time window
2. Identify traces with error status
3. Call `query_trace_spans` with a specific trace ID to get the full span tree
4. Display the request flow showing which span failed and in which service

**Expected:** The trace should show the frontend calling the product catalog service (or checkout calling it), with the final span showing a connection failure — gRPC `UNAVAILABLE` or connection refused.

## Step 4: Check Deployment State

Confirm the root cause by checking the deployment state.

```
Show me the release binding details for the "productcatalog" component in the
"development" environment. Is it running? How many replicas are configured?
```

**What agent will do:**
1. Call `get_release_binding` (Control Plane MCP) for the productcatalog component's development release binding
2. Display the current replica count, resource configuration, and status

**Expected:** The assistant should report that the product catalog has **0 replicas** — confirming why all dependent services are failing.

## Step 5: Fix and Verify

Ask the AI assistant to fix the issue and verify recovery.

```
Update the productcatalog release binding to set replicas back to 1.
```

**What agent will do:**
1. Call `update_release_binding` (Control Plane MCP) to set the productcatalog replicas to 1
2. Confirm the update was applied

Wait a minute for the service to come back up, then verify:

```
Check the logs again for the last 2 minutes. Are the errors resolved?
Are there any new traces showing successful requests?
```

**What agent will do:**
1. Call `query_component_logs` for the affected components over the last 2 minutes
2. Call `query_traces` to find recent successful traces
3. Confirm the errors have stopped and requests are completing successfully

## MCP Tools Used

| Tool | MCP Server | Purpose |
|------|------------|---------|
| `list_components` | Control Plane | Discover services in the project |
| `query_component_logs` | Observability | Query logs filtered by severity and time |
| `query_traces` | Observability | Find distributed traces for failed requests |
| `query_trace_spans` | Observability | Inspect individual spans within a trace |
| `get_release_binding` | Control Plane | Check component replica count and deployment status |
| `update_release_binding` | Control Plane | Fix the replica count to restore the service |

## Next Steps

- Try the [Build Failure Diagnosis](../build-failures/) guide to troubleshoot CI/CD issues
- Try the [Resource Optimization](../resource-optimization/) guide to right-size your deployments



File: samples/mcp/resource-optimization/README.md
---
# Resource Optimization with OpenChoreo MCP Server

This guide walks you through a resource optimization scenario using the OpenChoreo MCP server and AI assistants. You'll intentionally over-provision services in the GCP Microservices Demo, then use AI-assisted analysis to detect the waste and right-size the deployments.

## Prerequisites

Before starting this guide, ensure you have completed all [prerequisites](../README.md#prerequisites)

Additionally, you need:

1. **GCP Microservices Demo deployed** — follow the [GCP Microservices Demo](../../gcp-microservices-demo/) sample to deploy the Online Boutique application
2. **Observability plane** configured and running — see [Observability & Alerting](https://openchoreo.dev/docs/platform-engineer-guide/observability-alerting/) for setup instructions
3. **Both MCP servers configured** — you need both the Control Plane and Observability Plane MCP servers connected to your AI assistant. See the [Configuration Guide](https://openchoreo.dev/docs/ai/mcp-servers)

## What You'll Learn

- How to inspect current resource allocation for release bindings using MCP tools
- How to query actual CPU and memory usage metrics
- How to use AI assistants to compare allocation vs usage and detect waste
- How to get right-sizing recommendations and apply them via MCP

## Scenario: Over-Provisioned Microservices

In real clusters, services often get allocated far more CPU and memory than they actually need — either from copy-pasting defaults or cautious initial sizing. We'll simulate this by patching several services with excessive resource requests, then use the AI assistant to find and fix the waste.

### Architecture context

```
frontend (over-provisioned: 2 CPU, 2Gi memory)
checkout (over-provisioned: 2 CPU, 2Gi memory)
cart     (over-provisioned: 1 CPU, 1Gi memory)
```

These lightweight services typically use a fraction of these resources.

## Step 1: Introduce Over-Provisioning

Patch the ReleaseBindings with excessive resource allocations. This is the OpenChoreo-native way to configure resources — patching deployments directly would be overwritten by the controllers.

```bash
# Over-provision frontend: 2 CPU / 2Gi memory
kubectl patch releasebinding frontend-development -n default \
  --type=merge -p '{
  "spec": {"componentTypeEnvironmentConfigs": {
    "resources": {"requests": {"cpu": "2", "memory": "2Gi"},
                  "limits": {"cpu": "2", "memory": "2Gi"}}}}}'

# Over-provision checkout: 2 CPU / 2Gi memory
kubectl patch releasebinding checkout-development -n default \
  --type=merge -p '{
  "spec": {"componentTypeEnvironmentConfigs": {
    "resources": {"requests": {"cpu": "2", "memory": "2Gi"},
                  "limits": {"cpu": "2", "memory": "2Gi"}}}}}'

# Over-provision cart: 1 CPU / 1Gi memory
kubectl patch releasebinding cart-development -n default \
  --type=merge -p '{
  "spec": {"componentTypeEnvironmentConfigs": {
    "resources": {"requests": {"cpu": "1", "memory": "1Gi"},
                  "limits": {"cpu": "1", "memory": "1Gi"}}}}}'
```

Wait a couple of minutes for the pods to restart and for usage metrics to start flowing.

## Step 2: Inspect Resource Allocation

Ask the AI assistant to check the current resource configuration across the project.

```
Show me the resource configuration (CPU and memory requests and limits) from
the release bindings for all components in the "default" namespace,
"gcp-microservice-demo" project.
```

**What agent will do:**
1. Call `list_components` (Control Plane MCP) to discover all components in the project
2. Call `list_release_bindings` (Control Plane MCP) to discover release bindings of each component
3. Call `get_release_binding` (Control Plane MCP) for each release binding
4. Display a summary of resource allocations across all components

**Expected:** The assistant should show that **frontend**, **checkout**, and **cart** have significantly higher resource allocations than the other services.

## Step 3: Query Actual Resource Usage

Now compare the allocations against what the services are actually consuming.

```
Query the CPU and memory usage metrics for the frontend, checkout, and cart
components in the "default" namespace, "gcp-microservice-demo" project,
"development" environment over the last 15 minutes. Compare with their
configured limits.
```

**What agent will do:**
1. Call `query_resource_metrics` (Observability MCP) for each of the three components
2. Display actual CPU and memory consumption alongside configured requests/limits
3. Highlight the gap between allocation and usage

**Expected:** The metrics should show that actual usage is a small fraction of the allocated resources — e.g., frontend using ~50m CPU out of 2000m allocated, or ~100Mi memory out of 2Gi allocated.

## Step 4: Get Right-Sizing Recommendations

Ask the AI assistant to analyze the waste and suggest optimal values.

```
Based on the actual usage data, these services look over-provisioned.
Suggest optimal CPU and memory requests and limits for frontend, checkout,
and cart. Include a safety buffer and explain your reasoning.
```

**What agent will do:**
1. Compare actual usage patterns against current allocations
2. Calculate recommended values with appropriate headroom (e.g., 2x peak usage for requests, 3x for limits)
3. Provide specific values for each service
4. Estimate the resource savings

## Step 5: Apply the Recommendations

Apply the optimized resource configuration using the MCP server.

```
Update the release bindings for frontend, checkout, and cart with the recommended resource values.
```

**What agent will do:**
1. Call `update_release_binding` (Control Plane MCP) for each component with the new resource values
2. Confirm each update was applied successfully

## Step 6: Verify the Changes

Confirm the new configuration is in place and the services are healthy.

```
Show me the updated release binding details for frontend, checkout, and cart.
Confirm the resource values were applied correctly and check if the components are running.
```

**What agent will do:**
1. Call `get_release_binding` (Control Plane MCP) for each component to confirm the new values
2. Report on the deployment status and whether the components are running

**Expected:** All three services should be running with the optimized resource allocations and no resource-related restarts.

## MCP Tools Used

| Tool | MCP Server | Purpose |
|------|------------|---------|
| `list_components` | Control Plane | Discover services in the project |
| `list_release_bindings` | Control Plane | Discover release bindings for each component |
| `get_release_binding` | Control Plane | Inspect resource allocation per component |
| `query_resource_metrics` | Observability | Query actual CPU and memory usage |
| `update_release_binding` | Control Plane | Apply optimized resource values |

## Next Steps

- Try the [Log Analysis & Debugging](../log-analysis/) guide to debug cascading failures
- Try the [Build Failure Diagnosis](../build-failures/) guide to troubleshoot CI/CD issues



File: samples/mcp/service-deployment/README.md
---
# Service Deployment with OpenChoreo MCP Server

This guide demonstrates how to deploy a REST API service from source code to production on OpenChoreo using the MCP server and AI assistants.

## Prerequisites

Before starting this guide, ensure you have completed all [prerequisites](../README.md#prerequisites)

Additionally, for service deployment you need:

1. **OpenChoreo instance** with at least two environments configured (development and production)
   - If you need to create environments, see the [platform configuration samples](../../platform-config/new-environments/)
2. **Component workflows** configured (Docker or Buildpacks)
   - Make sure you've installed the workflow plane. See [Setup Workflow Plane](https://openchoreo.dev/docs/getting-started/try-it-out/on-k3d-locally/#step-6-setup-workflow-plane-optional) guide.

## Deployment Guides

Choose the approach that best fits your workflow:

### 1. [Step-by-Step Guide](./step-by-step/)

A guided walkthrough with explicit prompts for each step. Perfect if you want:
- Clear, structured instructions
- Explicit prompts to copy and paste
- Step-by-step verification checkpoints

**Time:** 15-20 minutes

### 2. [Developer Chat](./developer-chat/)

A natural conversation-based deployment. Perfect if you want:
- Conversational interaction with the AI assistant
- More flexible, exploratory workflow
- Natural language deployment process

**Time:** 15-20 minutes

## What You'll Learn

Both guides will teach you how to:
- Create projects and components using AI assistants
- Configure Docker build workflows from source repositories
- Trigger and monitor builds programmatically
- Deploy services to development environments
- Promote services through the deployment pipeline (development → staging → production)
- Monitor component health and status
- Manage the complete service lifecycle through natural language

## Scenario Overview

In both guides, you'll deploy a simple "greeter" service:
- **Backend**: Go REST API service that responds with greeting messages
- **Source**: GitHub repository with Dockerfile
- **Deployment**: From source code to production through multiple environments



File: samples/mcp/service-deployment/developer-chat/README.md
---
# Deploying Service Component from Source - Developer Chat Guide

This guide demonstrates a natural conversation-based approach to deploying a service using the OpenChoreo MCP server. Instead of following explicit step-by-step instructions, you'll have a conversational interaction with your AI assistant to deploy your application.

## Prerequisites

Before starting, ensure you have completed all prerequisites from the [Service Deployment guide](../README.md).

**Time required:** 15-20 minutes

## Approach

This guide uses a conversational workflow where you interact naturally with your AI assistant. The assistant will:
- Ask clarifying questions when needed
- Use only OpenChoreo MCP tools (no curl, kubectl, or other external commands)
- Execute MCP tools efficiently and avoid unnecessary calls
- Reply concisely and keep the conversation focused
- Guide you through the deployment process through natural dialogue


### Step 1: Enter the Agent's system prompt

```
You're a useful agent to help make OpenChoreo tasks easier for OpenChoreo users. You can use only the OpenChoreo MCP server. Specifically, you can't use curl and kubectl. You may refer to OpenChoreo docs: https://openchoreo.dev/docs/. You may ask back the user questions when you want further input for a task.

You execute the MCP tools efficiently and avoid unnecessary tool calls. You reply concisely and keep the conversation clean. You don't generate .md files and other artifacts unless you're asked to.

To confirm, let me know whether you have access to the OpenChoreo MCP server.
```

The Agent will respond with the available MCP tools

### Step 2: Request Deployment

```
I want to deploy my Go REST API service on OpenChoreo. Source: https://github.com/openchoreo/sample-workloads/tree/main/service-go-greeter
The source contains a Dockerfile. You can use it for the deployment.
```

The agent will guide you through:
- Creating the project (if needed)
- Creating the component with Docker workflow configuration
- Triggering the build
- Monitoring build progress
- Verifying deployment
- Promoting to production (if desired)

The conversation will flow naturally based on your responses and the agent's questions.

## Tips for Best Results

1. **Be specific**: Provide clear answers to the agent's questions
2. **Verify steps**: Ask the agent to confirm what it's doing at each stage
3. **Monitor progress**: Request status updates on builds and deployments
4. **Ask questions**: If something is unclear, ask the agent to explain



File: samples/mcp/service-deployment/step-by-step/README.md
---

# Deploying Service Component from Source - Step-by-Step Guide

This comprehensive guide walks you through the complete lifecycle of deploying an application using the OpenChoreo MCP server - from creating a project to deploying a REST API service to production.

## Prerequisites

Before starting, ensure you have completed all prerequisites from the [Service Deployment guide](../README.md).

**Time required:** 15-20 minutes

## Scenario Overview

In this scenario, you'll deploy a simple "greeter" service:
- **Backend**: Go REST API service that responds with greeting messages

You'll learn to:
1. Verify prerequisites and infrastructure
2. Create a new project
3. Create a service component and configure Docker build workflow
4. Trigger builds from source
5. Deploy to development environment
6. Test the application
7. Promote to production
8. Monitor deployment status

## Step 1: Verify Prerequisites

First, verify that your OpenChoreo instance has the necessary infrastructure.
Prompt:
```
List the environments in my "default" namespace
```

**Expected:** You should see at least "development" environment. If not, create one following the [platform configuration samples](../../../platform-config/new-environments/).

## Step 2: Create a New Project

Let's create a project called "greeter" for our application.

Prompt:
```
Create a new project called "greeter" in the "default" namespace with description "Simple greeter service in Go"
```

**What agent will do:**
1. Call `create_project` with the provided details
2. Confirm project creation
3. Show the project details

## Step 3: Create Component and Configure Build Workflow

Now let's create the greeter service component and configure its build workflow.

Prompt:
```
Create a component called "greeter-service" in the greeter project. 
It should be a deployment/service type, listening on port 9090, 
with 1 replica, and publicly exposed. Configure it to build from 
the GitHub repository https://github.com/openchoreo/sample-workloads,
using the Docker workflow, with the source in /service-go-greeter directory.
```

**What agent will do:**
1. Check `create_component` tool schema to understand required parameters
2. Call `list_component_types`, `list_component_workflows`, `get_component_workflow_schema` to identify available component types and workflow schemas to generate component creation request
3. Call `create_component` with generated configuration
4. Show the component details 

**Checkpoint:** The greeter-service component should be created with its build workflow configured.

## Step 4: Trigger Build

Now let's build the container image for our greeter service.

### Build Greeter Service

Prompt:
```
Trigger a build for the greeter-service component in the greeter project using the main branch
```

**What agent will do:**
1. Call `trigger_component_workflow` with the component details
2. Return a build ID for tracking
3. Provide commands to monitor build progress

### Monitor Build Progress

Prompt:
```
What's the status of the greeter-service build? Check periodically until the build finishes
```

**What agent will do:**
1. Call `list_component_workflow_runs` for the component
2. Show build status, duration, and outcome
3. Alert if the build failed

**Checkpoint:** The build should complete successfully. If it fails, review build logs and fix issues.
**Checkpoint:** Since the component creation tool enables automatic deployment, a release should be automatically triggered on the development environment

## Step 5: Verify Deployment

Let's verify that the greeter service is running correctly.

### Check Component Status

Prompt:
```
Show me the deployment status of the greeter-service in the greeter project
```

**What agent will do:**
1. Call `get_component_workloads`, `list_release_bindings` for the component
2. Show pod status, health, and resource usage
3. Highlight any issues

### Get Access URL

Prompt:
```
What is the endpoint URL for my greeter service in development? The gateway is running on the port 19080
```

**What agent will do:**
1. Extract endpoint information from component details
2. Provide formatted URL for accessing the service

### Test the Service

**Sample Curl**
```
curl http://development-default.openchoreoapis.localhost:19080/greeter/greet?name=World
```

**Expected response:**
```
Hello, World
```

**Checkpoint:** The greeter service should be accessible and responding correctly.

## Step 6: Promote to Production

After testing in development, let's promote the greeter service to production.

### Promote the Service

Prompt:
```
Promote the greeter-service up to the production environment
```

**What agent will do:**
1. Call `promote_component` with source and target environments 2 times (development --> staging --> production)
2. Confirm the promotion
3. Show deployment status in production

**Checkpoint:** The greeter service should be running in production.

## Congratulations! 🎉

You've successfully deployed a service using the OpenChoreo MCP server! You now know how to:

- Create projects and components using AI assistants
- Configure Docker build workflows from source repositories
- Trigger and monitor builds programmatically
- Promote services through the deployment pipeline
- Monitor component health and status
- Manage the complete service lifecycle through natural language

**Share your success** with the community on [Slack](https://cloud-native.slack.com/archives/C0ABYRG1MND)!



File: samples/platform-config/new-deployment-pipeline/README.md
---
# Create a new Deployment Pipeline
This sample demonstrates how to create a new Deployment Pipeline in Choreo. 

The Deployment Pipeline resource kind represents an ordered set of environments that a deployment will go through to reach a critical environment. 

In this sample the new deployment pipeline facilitates promoting from development to qa, qa to pre-production, and then from pre-production to production environments which were created earlier.

## Deploy in Choreo
Use the following command to create the new deployment pipeline.

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/platform-config/new-deployment-pipeline/deployment-pipeline.yaml
```



File: samples/occ-cli/go-greeter-manual-deploy/README.md
---
# Go Greeter Service (Manual Deploy with occ CLI)

## Overview

This sample demonstrates how to deploy a Go REST service in OpenChoreo using the `occ` CLI with manual control over each stage: build, deploy, and promote.

The component is created with `autoDeploy: false`, so builds and deployments must be triggered explicitly.

The service exposes one REST endpoint.

Exposed REST endpoints:

### Greet a user

**Endpoint:** `/greeter/greet`
**Method:** `GET`
**Functionality:** Sends a greeting to the user.

The source code is available at:
https://github.com/openchoreo/sample-workloads/tree/main/service-go-greeter

## Prerequisites

- A running OpenChoreo cluster (see [Getting Started](https://openchoreo.dev/docs/getting-started/quick-start-guide/))
- The `occ` CLI installed and configured (see [CLI Installation](https://openchoreo.dev/docs/developer-guide/cli-installation/))
- Logged in via `occ login`
- [`yq`](https://github.com/mikefarah/yq#install) installed (used to extract the invoke URL in Step 5)

## Step 1: Apply the Component

The following command will create the component in OpenChoreo with `autoDeploy: false`. This registers the component but does not trigger a build or deployment automatically.

```bash
occ apply -f samples/occ-cli/go-greeter-manual-deploy/greeter-service.yaml
```

Verify the component was created:

```bash
occ component list
```

## Step 2: Trigger a Workflow Run (Build)

Run the component's configured workflow to build the container image:

```bash
occ component workflow run greeter-service
```

## Step 3: Monitor the Build

List workflow runs for the component:

```bash
occ component workflowrun list greeter-service
```

Follow the build logs:

```bash
occ component workflowrun logs greeter-service
```

> [!NOTE]
> The Docker build typically takes 3-5 minutes depending on network speed and system resources.

## Step 4: Deploy to Development

Once the build succeeds, deploy the component to the root environment (development):

```bash
occ component deploy greeter-service
```

Check the release bindings:

```bash
occ releasebinding list
```

## Step 5: Test the Application

Wait for the release binding status to show `Ready` before proceeding:

```bash
occ releasebinding list
```

Get the invoke URL from the release binding status and test the endpoint:

```bash
INVOKE_URL=$(occ releasebinding get greeter-service-development | yq '.status.endpoints[0].externalURLs.http | .scheme + "://" + .host + ":" + (.port | tostring) + .path')
```

```bash
curl "$INVOKE_URL/greeter/greet"
```

```bash
curl "$INVOKE_URL/greeter/greet?name=Alice"
```

## Step 6: Check Component Logs

Verify the component is running by checking its runtime logs:

```bash
occ component logs greeter-service
```

```bash
# Logs from a specific environment
occ component logs greeter-service --env development
```

## Step 7: Promote to Staging

Promote the component to the next environment:

```bash
occ component deploy greeter-service --to staging
```

Check the release binding status:

```bash
occ releasebinding list
```

## Step 8: Promote to Production

```bash
occ component deploy greeter-service --to production --set spec.componentTypeEnvironmentConfigs.replicas=2
```

## Clean Up

Remove all resources:

```bash
occ component delete greeter-service
```



File: samples/platform-config/new-environments/README.md
---
# Create a new Environment
This guide demonstrates how to create new environments in Choreo. 

The Environment resource kind helps organize and manage different stages of the application lifecycle, such as development, testing, and production. The environment is bound to a specific data plane in Choreo. 

We will create four such environments in your namespace.

### Environment Hierarchy

| Environment      | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| 1. development    | Shared development, team-wide feature branches, early integrations      |
| 2. qa             | Functional, regression, integration testing (often automated)           |
| 3. pre-production | Staging environment closely mirrors production (infra, secrets, data)   |
| 4. production     | Live, customer-facing traffic; change-controlled, monitored 

## Deploy in Choreo
Use the following command to create new environments.

```bash
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/platform-config/new-environments/development-environment.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/platform-config/new-environments/qa-environment.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/platform-config/new-environments/pre-production-environment.yaml
kubectl apply -f https://raw.githubusercontent.com/openchoreo/openchoreo/main/samples/platform-config/new-environments/production-environment.yaml
```



File: samples/workflows/aws-rds-postgres/README.md
---
# AWS RDS PostgreSQL Create — Generic Workflow Sample

This sample demonstrates a self-service Generic Workflow that lets a developer quickly spin up a throwaway AWS RDS PostgreSQL instance for feature development or testing — without involving the platform team. Fill in a few parameters, trigger the workflow, and get a ready-to-use connection string at the end.

The instance is a minimal, publicly accessible `db.t3.micro` (free-tier eligible) — sized for dev/test, not production. The workflow clones this repository at runtime to execute the Terraform files in `terraform/`. Terraform state is stored in S3 so the same instance can be updated or destroyed later.

---

## Pipeline Overview

```
WorkflowRun
    │
    ▼
[clone-step]    — git clone the configured repo/branch to get terraform/
    │
    ▼
[setup-step]    — create the S3 state bucket if it does not already exist
    │
    ▼
[init-step]     — terraform init with S3 backend
    │
    ▼
[plan-step]     — terraform plan (dry run, visible in logs)
    │
    ▼
[apply-step]    — terraform apply -auto-approve; save outputs to shared volume
    │
    ▼
[report-step]   — print host, port, database, username, password, connection string
```

---

## Infrastructure Provisioned

| Resource | Details |
|----------|---------|
| `aws_db_instance` | PostgreSQL `db.t3.micro` (free-tier eligible), 20 GiB gp2 (AWS minimum), single-AZ |
| `aws_db_subnet_group` | Uses subnets from the default VPC |
| `aws_security_group` | Allows port 5432 inbound from `0.0.0.0/0` |

The instance is **publicly accessible** so you can connect directly from your workstation to verify it. For production use, set `publicly_accessible = false` in `terraform/main.tf` and restrict the security group `cidr_blocks` to your application's IP range.

---

## Prerequisites

### 1. IAM permissions

The IAM user needs two policy statements. The S3 bucket for Terraform state is created automatically by the workflow on first run — no manual bucket creation needed.

**RDS, EC2, and S3:**
```json
{
  "Effect": "Allow",
  "Action": [
    "rds:CreateDBInstance",
    "rds:DeleteDBInstance",
    "rds:DescribeDBInstances",
    "rds:AddTagsToResource",
    "rds:ListTagsForResource",
    "rds:CreateDBSubnetGroup",
    "rds:DescribeDBSubnetGroups",
    "rds:DeleteDBSubnetGroup",
    "ec2:DescribeVpcs",
    "ec2:DescribeVpcAttribute",
    "ec2:DescribeSubnets",
    "ec2:DescribeSecurityGroups",
    "ec2:DescribeNetworkInterfaces",
    "ec2:CreateSecurityGroup",
    "ec2:AuthorizeSecurityGroupIngress",
    "ec2:AuthorizeSecurityGroupEgress",
    "ec2:RevokeSecurityGroupEgress",
    "ec2:DeleteSecurityGroup",
    "ec2:CreateTags",
    "s3:CreateBucket",
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket",
    "s3:DeleteObject"
  ],
  "Resource": "*"
}
```

### 2. Kubernetes Secret

Create the secret in the workflow execution namespace — `workflows-<namespace>` where `<namespace>` is the namespace your `WorkflowRun` is applied in (e.g. `workflows-default`).

The secret holds three values:
- `accessKeyId` — AWS access key ID
- `secretAccessKey` — AWS secret access key
- `dbPassword` — master password for the PostgreSQL instance

```bash
kubectl create secret generic aws-rds-credentials \
  --from-literal=accessKeyId=<your-access-key-id> \
  --from-literal=secretAccessKey=<your-secret-access-key> \
  --from-literal=dbPassword=<your-db-password> \
  --namespace=workflows-default
```

> The DB password is stored in a Kubernetes Secret and injected into the workflow as an environment variable. It is **not** passed as a plain workflow parameter.

---

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `git.repoUrl` | No | `https://github.com/openchoreo/openchoreo.git` | Git repository URL (HTTPS) that contains the Terraform files. Override to use your own repo. |
| `git.branch` | No | `main` | Branch or tag to check out |
| `git.tfPath` | No | `samples/workflows/aws-rds-postgres/terraform` | Relative path inside the cloned repo to the directory containing the Terraform files |
| `aws.region` | No | `us-east-1` | AWS region for the RDS instance |
| `aws.credentialsSecret` | Yes | — | Name of the Kubernetes Secret (see Prerequisites) |
| `tfState.s3Bucket` | Yes | — | S3 bucket name for Terraform state. Created automatically on first run if it does not exist. |
| `db.identifier` | Yes | — | Unique RDS instance identifier (e.g. `my-app-db`). Also used as the S3 state key prefix. |
| `db.name` | Yes | — | Initial database name inside the instance |
| `db.username` | Yes | — | Master username |
| `db.engineVersion` | No | `"16"` | PostgreSQL major version (`"16"`, `"15"`, etc.) |

---

## How to Run

```bash
# 1. Apply the ClusterWorkflowTemplate and Workflow CRs
kubectl apply -f aws-rds-postgres-create.yaml
```

Edit the `WorkflowRun` section at the bottom of the file with your values, then apply, or create a separate `WorkflowRun`:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: my-app-db-run
spec:
  workflow:
    name: aws-rds-postgres-create
    parameters:
      # Override these to point to your own repo/branch/terraform path.
      git:
        repoUrl: "https://github.com/openchoreo/openchoreo.git"
        branch: "main"
        tfPath: "samples/workflows/aws-rds-postgres/terraform"
      aws:
        region: "us-east-1"
        credentialsSecret: "aws-rds-credentials"
      tfState:
        s3Bucket: "openchoreo-rds-tfstate"
      db:
        identifier: "my-app-db"
        name: "myappdb"
        username: "dbadmin"
        engineVersion: "16"
```

---

## Example Output

```
=================================================
  AWS RDS PostgreSQL Instance Created
=================================================
Host:              my-app-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
Port:              5432
Database:          myappdb
Username:          dbadmin
ARN:               arn:aws:rds:us-east-1:111122223333:db:my-app-db
-------------------------------------------------
Connection String (template):
  postgresql://dbadmin:<password>@my-app-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com:5432/myappdb

NOTE: Password is stored in the 'aws-rds-credentials'
      Kubernetes Secret under the 'dbPassword' key.
      Retrieve it with:
      kubectl get secret aws-rds-credentials \
        -o jsonpath='{.data.dbPassword}' | base64 -d
=================================================

NOTE: The instance is publicly accessible on port 5432.
```

---

## Deleting the Instance

Use the companion `aws-rds-postgres-delete` workflow to destroy the instance and all associated AWS resources (security group, subnet group). It reads the same Terraform state file from S3, so no manual cleanup is needed.

```bash
# Apply the delete ClusterWorkflowTemplate and Workflow CRs
kubectl apply -f aws-rds-postgres-delete.yaml
```

Edit the `WorkflowRun` section at the bottom of `aws-rds-postgres-delete.yaml` with the **same parameter values used when creating the instance**, then apply:

```bash
kubectl apply -f aws-rds-postgres-delete.yaml
```

> **Important:** `db.identifier`, `tfState.s3Bucket`, and `aws.region` must exactly match the values used during creation — Terraform uses these to locate the correct state file.

---

## Terraform State

State is stored at:
```
s3://<tfState.s3Bucket>/rds/<db.identifier>/terraform.tfstate
```

Each `db.identifier` gets its own isolated state key, so running the workflow for a different identifier does not affect existing instances.



File: samples/workflows/github-stats-report/README.md
---
# GitHub Stats Report — Generic Workflow Sample

This sample demonstrates a Generic Workflow that fetches repository statistics from the GitHub public API, transforms the raw response into a concise summary, and prints a formatted report. It has no dependency on any Component and serves as a clear example of how Generic Workflows differ from CI Workflows.

---

## Pipeline Overview

```
WorkflowRun
    │
    ▼
[fetch-step]   — curl GitHub API → raw.json (shared volume)
    │
    ▼
[transform-step] — jq extracts fields → stats.json (shared volume)
    │
    ▼
[report-step]  — formats and prints the report (table or JSON)
```

## Files

| File | Kind | Description |
|------|------|-------------|
| `cluster-workflow-template-github-stats-report.yaml` | `ClusterWorkflowTemplate` | Argo Workflows template with the three execution steps |
| `workflow-github-stats-report.yaml` | `Workflow` | OpenChoreo CR — defines the parameter schema and references the template |
| `workflow-run-github-stats-report.yaml` | `WorkflowRun` | Triggers a run with specific parameter values |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `source.org` | `openchoreo` | GitHub organization name |
| `source.repo` | `openchoreo` | GitHub repository name |
| `output.format` | `table` | Output format: `table` (human-readable) or `json` (machine-readable) |

## How to Run

Deploy the resources in order:

```bash
# 1. Deploy the ClusterWorkflowTemplate to the Workflow Plane
kubectl apply -f cluster-workflow-template-github-stats-report.yaml

# 2. Deploy the Workflow CR to the Control Plane
kubectl apply -f workflow-github-stats-report.yaml

# 3. Trigger an execution by creating a WorkflowRun
kubectl apply -f workflow-run-github-stats-report.yaml
```

To report on a different repository, override the parameters in your `WorkflowRun`:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: my-stats-run
spec:
  workflow:
    name: github-stats-report
    parameters:
      source:
        org: "kubernetes"
        repo: "kubernetes"
      output:
        format: "json"
```

## Example Output (table format)

```
=============================
  GitHub Repository Report
=============================
Name:         openchoreo/openchoreo
Description:  The OpenChoreo internal developer platform
Language:     Go
Stars:        312
Forks:        48
Open Issues:  27
License:      Apache License 2.0
Topics:       platform-engineering, kubernetes, developer-platform
Created:      2023-11-01T08:00:00Z
Updated:      2026-02-28T14:32:11Z
=============================
```



File: samples/workflows/scm-create-repo/README.md
---
# SCM Create Repository — Generic Workflow Sample

This sample demonstrates Generic Workflows that create a new source code repository via a cloud SCM provider's API. Each provider has its own self-contained YAML file that includes all three required resources: the Argo `ClusterWorkflowTemplate`, the OpenChoreo `Workflow`, and a sample `WorkflowRun`.

The workflows have no dependency on any Component and can be triggered manually.

---

## Available Providers

| File | Provider | Description |
|------|----------|-------------|
| [`github-create-repo.yaml`](./github-create-repo.yaml) | GitHub | Creates a repository under a GitHub organization |
| [`codecommit-create-repo.yaml`](./codecommit-create-repo.yaml) | AWS CodeCommit | Creates a repository in an AWS CodeCommit region |

---

## Pipeline Overview

Both workflows follow the same two-step pattern:

```
WorkflowRun
    │
    ▼
[create-step]  — calls the provider API → response.json (shared volume)
    │
    ▼
[report-step]  — prints repository details (name, clone URLs, etc.)
```

---

## GitHub

### Prerequisites

The workflow authenticates with GitHub using a Personal Access Token (PAT). The token must have the **`repo`** scope (for private repositories) or **`public_repo`** scope (for public repositories). If creating repositories under an organization, the token also needs the **`admin:org`** scope.

The secret must be created in the workflow plane namespace where Argo executes the workflow steps — `workflows-<namespace>` (e.g. `workflows-default` if your `WorkflowRun` is in the `default` namespace):

```bash
kubectl create secret generic github-token \
  --from-literal=token=<your-github-pat> \
  --namespace=workflows-default
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `github.owner` | Yes | — | GitHub organization or user that will own the repository |
| `github.tokenSecret` | Yes | — | Name of the Kubernetes Secret containing the PAT under the key `token` (e.g. `github-token`) |
| `repo.name` | Yes | — | Name of the repository to create |
| `repo.description` | No | `""` | Short description of the repository |
| `repo.visibility` | No | `private` | Repository visibility: `public` or `private` |
| `repo.autoInit` | No | `"true"` | Initialize the repository with an empty README: `"true"` or `"false"` |
| `repo.gitignoreTemplate` | No | `""` | Gitignore template to apply (e.g. `Go`, `Python`, `Node`) |
| `repo.licenseTemplate` | No | `""` | License template to apply (e.g. `mit`, `apache-2.0`) |

### How to Run

```bash
# 1. Apply all three resources (ClusterWorkflowTemplate, Workflow, and WorkflowRun)
kubectl apply -f github-create-repo.yaml
```

To customise the run, edit the `WorkflowRun` section at the bottom of `github-create-repo.yaml` before applying, or create a separate `WorkflowRun`:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: my-github-repo-run
spec:
  workflow:
    name: scm-github-create-repo
    parameters:
      github:
        owner: "my-org"
        tokenSecret: "github-token"
      repo:
        name: "my-service"
        description: "Backend service for the payments platform"
        visibility: "private"
        autoInit: "true"
        gitignoreTemplate: "Go"
        licenseTemplate: "apache-2.0"
```

### Example Output

```
=================================
  GitHub Repository Created
=================================
Name:           my-org/my-service
URL:            https://github.com/my-org/my-service
Clone (HTTPS):  https://github.com/my-org/my-service.git
Clone (SSH):    git@github.com:my-org/my-service.git
Visibility:     private
Default Branch: main
Description:    Backend service for the payments platform
Created At:     2026-03-06T10:00:00Z
=================================
```

### Common Gitignore Templates

| Language / Framework | Value |
|----------------------|-------|
| Go | `Go` |
| Python | `Python` |
| Node.js | `Node` |
| Java | `Java` |
| Rust | `Rust` |

For the full list see the [GitHub gitignore templates repository](https://github.com/github/gitignore).

### Common License Templates

| License | Value |
|---------|-------|
| MIT | `mit` |
| Apache 2.0 | `apache-2.0` |
| GNU GPLv3 | `gpl-3.0` |
| BSD 2-Clause | `bsd-2-clause` |

For the full list see the [GitHub license API](https://docs.github.com/en/rest/licenses/licenses).

---

## AWS CodeCommit

### Prerequisites

The workflow authenticates with AWS using an IAM user's access key. The IAM user must have the **`codecommit:CreateRepository`** permission.

Create the secret in the workflow plane namespace:

```bash
kubectl create secret generic aws-credentials \
  --from-literal=accessKeyId=<your-access-key-id> \
  --from-literal=secretAccessKey=<your-secret-access-key> \
  --namespace=workflows-default
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `aws.region` | Yes | — | AWS region where the repository will be created (e.g. `us-east-1`) |
| `aws.credentialsSecret` | Yes | — | Name of the Kubernetes Secret containing `accessKeyId` and `secretAccessKey` keys (e.g. `aws-credentials`) |
| `repo.name` | Yes | — | Name of the CodeCommit repository to create |
| `repo.description` | No | `""` | Short description of the repository |

### How to Run

```bash
# 1. Apply all three resources (ClusterWorkflowTemplate, Workflow, and WorkflowRun)
kubectl apply -f codecommit-create-repo.yaml
```

To customise the run, edit the `WorkflowRun` section at the bottom of `codecommit-create-repo.yaml` before applying, or create a separate `WorkflowRun`:

```yaml
apiVersion: openchoreo.dev/v1alpha1
kind: WorkflowRun
metadata:
  name: my-codecommit-repo-run
spec:
  workflow:
    name: scm-codecommit-create-repo
    parameters:
      aws:
        region: "us-east-1"
        credentialsSecret: "aws-credentials"
      repo:
        name: "my-service"
        description: "Backend service for the payments platform"
```

### Example Output

```
=================================
  CodeCommit Repository Created
=================================
Name:          my-service
Description:   Backend service for the payments platform
Repository ID: a1b2c3d4-5678-90ab-cdef-EXAMPLE11111
ARN:           arn:aws:codecommit:us-east-1:111122223333:my-service
Clone (HTTPS): https://git-codecommit.us-east-1.amazonaws.com/v1/repos/my-service
Clone (SSH):   ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/my-service
Account ID:    111122223333
=================================
```

---

## Triggering a Run via the OpenChoreo Console

Each YAML file in this sample includes a `WorkflowRun` that can be applied directly with `kubectl`. Alternatively, runs can be triggered from the OpenChoreo Console:

1. Open the **OpenChoreo Console** and navigate to the **Catalog** and filter workflows
2. Find the workflow by name (e.g. `scm-github-create-repo` or `scm-codecommit-create-repo`) — it will be listed under the **Generic** type
3. Select the workflow and go to the **Runs** tab
4. Click **New Run** and fill in the parameter values in the YAML editor
5. Submit to trigger the execution



File: samples/workflows/README.md
---
# Workflow Samples

This directory contains Workflow definitions for OpenChoreo. Each subdirectory provides a self-contained workflow example with its own README.

---

## Available Workflows

| Directory | Description |
|-----------|-------------|
| [`aws-rds-postgres/`](./aws-rds-postgres/) | Provision and destroy AWS RDS PostgreSQL instances using Terraform |
| [`github-stats-report/`](./github-stats-report/) | Generate GitHub repository statistics reports |
| [`scm-create-repo/`](./scm-create-repo/) | Create repositories in GitHub or AWS CodeCommit |

See each subdirectory's README for usage details.



File: test-alerts-incidents.md
---
# Alert & Incident Test Curls (development environment)

## Cluster resources

| Resource | Name | UID | Project |
|----------|------|-----|---------|
| Project | url-shortener | 25eccd80-3e99-4bf9-96ce-9ba6bd9088b7 | — |
| Component | frontend | 6d918b54-9f50-4eff-8226-83df187ccde0 | url-shortener |
| Component | api-service | 1935a545-856e-4bce-933f-59c0fe3e1742 | url-shortener |
| Component | analytics-service | 60d08490-64cb-4307-b1e0-d2fdfc5dbdd3 | url-shortener |
| Component | postgres | bf85bc08-5afc-456d-9fd0-7ca8670e7f2a | url-shortener |
| Component | redis | 4e0aab93-0a4d-422a-9168-e82fa139ee2e | url-shortener |
| Environment | development | bd6cfee8-354f-4476-8f3e-94a87c114681 | — |
| NotificationChannel | webhook-notification-channel-development | — | — |
| Existing AlertRule | frontend-5xx-log-alert | (in dp-default-url-shortener-development-a16f373a) | url-shortener/frontend |
| Dataplane NS | dp-default-url-shortener-development-a16f373a | — | — |

## Prerequisites

```bash
# Port-forward the internal observer API (webhook endpoint)
kubectl port-forward svc/observer-internal -n openchoreo-observability-plane 8081:8081 &

export BASE_URL="http://observer.openchoreo.localhost:11080"
export INTERNAL_URL="http://localhost:8081"
export TOKEN=$(token)
export DP_NS="dp-default-url-shortener-development-a16f373a"
```

## Step 1: Create ObservabilityAlertRule CRs

The existing `frontend-5xx-log-alert` is already synced. Create additional rules for other url-shortener components in development.

### 1a. High memory — api-service

```bash
kubectl apply -f - <<'EOF'
apiVersion: openchoreo.dev/v1alpha1
kind: ObservabilityAlertRule
metadata:
  name: high-memory-api-service-dev
  namespace: dp-default-url-shortener-development-a16f373a
  labels:
    openchoreo.dev/component-uid: 1935a545-856e-4bce-933f-59c0fe3e1742
    openchoreo.dev/project-uid: 25eccd80-3e99-4bf9-96ce-9ba6bd9088b7
    openchoreo.dev/environment-uid: bd6cfee8-354f-4476-8f3e-94a87c114681
    openchoreo.dev/namespace: default
    openchoreo.dev/project: url-shortener
    openchoreo.dev/component: api-service
    openchoreo.dev/environment: development
spec:
  name: high-memory-api-service-dev
  description: "Memory usage exceeded 90% for api-service in development"
  severity: critical
  enabled: true
  source:
    type: metric
    metric: memory_usage
  condition:
    window: 5m
    interval: 1m
    operator: gt
    threshold: 90
  actions:
    notifications:
      channels:
        - webhook-notification-channel-development
    incident:
      enabled: true
EOF
```

### 1b. High CPU — analytics-service

```bash
kubectl apply -f - <<'EOF'
apiVersion: openchoreo.dev/v1alpha1
kind: ObservabilityAlertRule
metadata:
  name: high-cpu-analytics-dev
  namespace: dp-default-url-shortener-development-a16f373a
  labels:
    openchoreo.dev/component-uid: 60d08490-64cb-4307-b1e0-d2fdfc5dbdd3
    openchoreo.dev/project-uid: 25eccd80-3e99-4bf9-96ce-9ba6bd9088b7
    openchoreo.dev/environment-uid: bd6cfee8-354f-4476-8f3e-94a87c114681
    openchoreo.dev/namespace: default
    openchoreo.dev/project: url-shortener
    openchoreo.dev/component: analytics-service
    openchoreo.dev/environment: development
spec:
  name: high-cpu-analytics-dev
  description: "CPU usage exceeded 85% for analytics-service in development"
  severity: warning
  enabled: true
  source:
    type: metric
    metric: cpu_usage
  condition:
    window: 5m
    interval: 1m
    operator: gt
    threshold: 85
  actions:
    notifications:
      channels:
        - webhook-notification-channel-development
    incident:
      enabled: true
EOF
```

### 1c. Error logs — redis

```bash
kubectl apply -f - <<'EOF'
apiVersion: openchoreo.dev/v1alpha1
kind: ObservabilityAlertRule
metadata:
  name: error-log-redis-dev
  namespace: dp-default-url-shortener-development-a16f373a
  labels:
    openchoreo.dev/component-uid: 4e0aab93-0a4d-422a-9168-e82fa139ee2e
    openchoreo.dev/project-uid: 25eccd80-3e99-4bf9-96ce-9ba6bd9088b7
    openchoreo.dev/environment-uid: bd6cfee8-354f-4476-8f3e-94a87c114681
    openchoreo.dev/namespace: default
    openchoreo.dev/project: url-shortener
    openchoreo.dev/component: redis
    openchoreo.dev/environment: development
spec:
  name: error-log-redis-dev
  description: "Error log count exceeded threshold for redis in development"
  severity: warning
  enabled: true
  source:
    type: log
    query: "level:ERROR"
  condition:
    window: 10m
    interval: 1m
    operator: gt
    threshold: 5
  actions:
    notifications:
      channels:
        - webhook-notification-channel-development
    incident:
      enabled: true
EOF
```

### Verify all CRs

```bash
kubectl get observabilityalertrules -n $DP_NS
```

## Step 2: Fire Alert Webhooks

### 2a. 5xx logs — frontend (existing rule)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "frontend-development-def9a783-frontend-5xx-log-alert",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 8,
    "alertTimestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

### 2b. Memory spike — api-service (93.7%)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "high-memory-api-service-dev",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 93.7,
    "alertTimestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

### 2c. CPU spike — analytics-service (91.2%)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "high-cpu-analytics-dev",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 91.2,
    "alertTimestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

### 2d. Error logs — redis (12 errors)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "error-log-redis-dev",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 12,
    "alertTimestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

### 2e. Second memory spike — api-service (97.3%, 5 min later)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "high-memory-api-service-dev",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 97.3,
    "alertTimestamp": "'"$(date -u -v+5M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

### 2f. Second 5xx spike — frontend (10 min later)

```bash
curl -s -X POST "$INTERNAL_URL/api/v1alpha1/alerts/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "frontend-development-def9a783-frontend-5xx-log-alert",
    "ruleNamespace": "'"$DP_NS"'",
    "alertValue": 15,
    "alertTimestamp": "'"$(date -u -v+10M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+10 minutes' +%Y-%m-%dT%H:%M:%SZ)"'"
  }' | jq .
```

## Step 3: Query Alerts

### 3a. All alerts in development

```bash
curl -s -X POST "$BASE_URL/api/v1alpha1/alerts/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "startTime": "'"$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "endTime": "'"$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "searchScope": {
      "namespace": "default",
      "environment": "development"
    },
    "limit": 50,
    "sortOrder": "desc"
  }' | jq .
```

### 3b. Alerts for api-service only

```bash
curl -s -X POST "$BASE_URL/api/v1alpha1/alerts/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "startTime": "'"$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "endTime": "'"$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "searchScope": {
      "namespace": "default",
      "project": "url-shortener",
      "component": "api-service",
      "environment": "development"
    },
    "limit": 20,
    "sortOrder": "desc"
  }' | jq .
```

### 3c. Alerts for frontend only

```bash
curl -s -X POST "$BASE_URL/api/v1alpha1/alerts/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "startTime": "'"$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "endTime": "'"$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "searchScope": {
      "namespace": "default",
      "project": "url-shortener",
      "component": "frontend",
      "environment": "development"
    },
    "sortOrder": "asc"
  }' | jq .
```

## Step 4: Query Incidents

### 4a. All incidents in development

```bash
curl -s -X POST "$BASE_URL/api/v1alpha1/incidents/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "startTime": "'"$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "endTime": "'"$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "searchScope": {
      "namespace": "default",
      "environment": "development"
    },
    "limit": 50,
    "sortOrder": "desc"
  }' | jq .
```

### 4b. Incidents for api-service

```bash
curl -s -X POST "$BASE_URL/api/v1alpha1/incidents/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "startTime": "'"$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '-1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "endTime": "'"$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)"'",
    "searchScope": {
      "namespace": "default",
      "project": "url-shortener",
      "component": "api-service",
      "environment": "development"
    },
    "sortOrder": "desc"
  }' | jq .
```

## Step 5: Update an Incident

Use an incident ID from step 4 results:

```bash
export INCIDENT_ID="<incident-id-from-step-4>"

# Acknowledge
curl -s -X PUT "$BASE_URL/api/v1alpha1/incidents/$INCIDENT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "acknowledged",
    "notes": "Investigating high resource usage"
  }' | jq .

# Resolve
curl -s -X PUT "$BASE_URL/api/v1alpha1/incidents/$INCIDENT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "resolved",
    "notes": "Scaled up replicas, usage normalized"
  }' | jq .
```

## Cleanup

```bash
kubectl delete observabilityalertrules -n $DP_NS \
  high-memory-api-service-dev \
  high-cpu-analytics-dev \
  error-log-redis-dev
```



File: tools/helm-gen/README.md
---
# helm-gen

A tool for generating Helm template files from Kubebuilder-generated manifests.

## Usage

### Command Line

```bash
# Basic usage
helm-gen -config-dir ./config -chart-dir ./install/helm/openchoreo-control-plane

# With custom controller subdirectory
helm-gen -config-dir ./config -chart-dir ./install/helm/openchoreo-control-plane -controller-subdir controller-manager
```

### Makefile Integration

The tool is integrated into the project's build system:

```bash
# Generate helm chart
make helm-generate.openchoreo-control-plane

# The makefile runs:
# 1. make manifests (to generate CRDs and RBAC)
# 2. helm-gen (to copy CRDs and generate RBAC)
# 3. Updates values.yaml with controller image settings
# 4. Runs helm dependency update and lint
```

## What It Generates

### 1. CRDs (Custom Resource Definitions)

- **Source**: `config/crd/bases/*.yaml`
- **Destination**: `<chart-dir>/crds/`

### 2. RBAC (Role-Based Access Control)

- **Source**: `config/rbac/role.yaml`
- **Destination**: `<chart-dir>/templates/controller-manager/controller-manager-role.yaml`


