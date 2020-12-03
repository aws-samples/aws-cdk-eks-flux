import base64
from aws_cdk import aws_eks as eks

class FluxcdCluster():
    def __init__(
            self,
            scope,            
            eks_base_cluster,
            git_user,
            git_password,
            git_repository,
            git_branch="master"
        ):            
        main_manifest = self._base_manifest(git_repository)
        main_manifest.append(self._secret_manifest(git_user,git_password))
        eks_manifest = eks.KubernetesManifest(
            scope=scope,
            id="fluxcd-main-manifest-new",
            cluster=eks_base_cluster,
            manifest=main_manifest
        )
    
    def _base64encode(self,string):
        return base64.b64encode(string.encode('ascii')).decode('ascii')

    
    def _secret_manifest(self,git_user,git_password):
        return {
                'apiVersion': 'v1', 
                'kind': 'Secret', 
                'metadata': {
                    'name': 'flux-git-auth', 
                    'namespace': 'default'
                },
                'data': {
                    'GIT_AUTHKEY' : self._base64encode(git_password),
                    'GIT_AUTHUSER' : self._base64encode(git_user)
                }, 
                'type': 'Opaque'
                }
    
    def _base_manifest(self,git_repository):
        return [{
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'memcached', 
                    'namespace': 'default'}, 
                    'spec': {
                        'replicas': 1, 
                        'selector': {
                            'matchLabels': {
                                'name': 'memcached'
                            }
                        }, 
                        'template': {
                            'metadata': {
                                'labels': {
                                    'name': 'memcached'
                                }
                            }, 
                            'spec': {
                                'nodeSelector': {
                                    'beta.kubernetes.io/os': 'linux'
                                }, 'containers': [{
                                    'name': 'memcached', 
                                    'image': 'memcached:1.5.20', 
                                    'imagePullPolicy': 'IfNotPresent', 
                                    'args': ['-m 512', '-I 5m', '-p 11211'], 
                                    'ports': [{
                                        'name': 'clients', 
                                        'containerPort': 11211
                                    }], 
                                    'securityContext': {
                                        'runAsUser': 11211, 
                                        'runAsGroup': 11211, 
                                        'allowPrivilegeEscalation': False
                                    }
                                }]
                            }
                        }
                    }
                }, 
            {
                'apiVersion': 'v1', 
                'kind': 'Service', 
                'metadata': {
                    'name': 'memcached', 
                    'namespace': 'default'
                }, 
                'spec': {
                    'ports': [{
                        'name': 'memcached', 
                        'port': 11211
                    }], 
                    'selector': {
                        'name': 'memcached'
                    }
                }
            }, 
            {
                'apiVersion': 'v1', 
                'kind': 'ServiceAccount', 
                'metadata': {
                    'labels': {
                        'name': 'flux'
                    }, 
                    'name': 'flux', 
                    'namespace': 'default'
                }
            }, 
            {
                'apiVersion': 'rbac.authorization.k8s.io/v1beta1', 
                'kind': 'ClusterRole', 
                'metadata': {
                    'labels': {
                        'name': 'flux'
                    }, 
                    'name': 'flux'
                }, 
                'rules': [{
                    'apiGroups': ['*'], 
                    'resources': ['*'], 
                    'verbs': ['*']
                    }, 
                    {'nonResourceURLs': ['*'], 
                    'verbs': ['*']
                }]
            }, 
            {
                'apiVersion': 'rbac.authorization.k8s.io/v1beta1', 
                'kind': 'ClusterRoleBinding', 
                'metadata': {
                    'labels': {
                        'name': 'flux'
                    }, 
                    'name': 'flux'
                }, 
                'roleRef': {
                    'apiGroup': 'rbac.authorization.k8s.io', 
                    'kind': 'ClusterRole', 
                    'name': 'flux'
                }, 
                'subjects': [{
                    'kind': 'ServiceAccount', 
                    'name': 'flux', 
                    'namespace': 'default'
                }]
            }, 
            {
                'apiVersion': 'apps/v1', 
                'kind': 'Deployment', 
                'metadata': {
                    'name': 'flux', 
                    'namespace': 'default'
                }, 
                'spec': {
                    'replicas': 1, 
                    'selector': {
                        'matchLabels': {
                            'name': 'flux'
                        }
                    }, 
                    'strategy': {
                        'type': 'Recreate'
                    }, 
                    'template': {
                        'metadata': {
                            'annotations': {
                                'prometheus.io/port': '3031'
                            }, 
                            'labels': {
                                'name': 'flux'
                            }
                        }, 
                        'spec': {
                            'nodeSelector': {
                                'beta.kubernetes.io/os': 'linux'
                            }, 
                            'serviceAccountName': 'flux', 
                            'volumes': [{
                                'name': 'git-key', 
                                'secret': {
                                    'secretName': 'flux-git-deploy', 
                                    'defaultMode': 256
                                }
                            }, 
                            {'name': 'git-keygen', 
                            'emptyDir': {
                                'medium': 'Memory'
                            }
                        }], 
                        'containers': [{
                            'name': 'flux', 
                            'image': 'docker.io/fluxcd/flux:1.21.0', 
                            'imagePullPolicy': 'IfNotPresent', 
                            'envFrom' : [{
                                'secretRef' : {
                                    'name' : 'flux-git-auth'
                                }
                            }],
                            'resources': {
                                'requests': {
                                    'cpu': '50m', 
                                    'memory': '64Mi'
                                }
                            }, 
                            'ports': [{
                                'containerPort': 3030
                            }], 
                            'livenessProbe': {
                                'httpGet': {
                                    'port': 3030, 
                                    'path': '/api/flux/v6/identity.pub'
                                }, 
                                'initialDelaySeconds': 5, 
                                'timeoutSeconds': 5
                            }, 
                            'readinessProbe': {
                                'httpGet': {
                                    'port': 3030, 
                                    'path': '/api/flux/v6/identity.pub'
                                }, 
                                'initialDelaySeconds': 5, 
                                'timeoutSeconds': 5
                            }, 
                            'volumeMounts': [{
                                'name': 'git-key', 
                                'mountPath': '/etc/fluxd/ssh', 
                                'readOnly': True
                                }, 
                                {'name': 'git-keygen', 
                                'mountPath': '/var/fluxd/keygen'
                                }], 
                            'args': ['--memcached-service=', 
                                    '--ssh-keygen-dir=/var/fluxd/keygen', 
                                    '--git-url=https://$(GIT_AUTHUSER):$(GIT_AUTHKEY)@' + git_repository, 
                                    '--git-branch=master',
                                    '--git-label=flux', 
                                    '--git-email=aws-example@users.noreply.github.com', 
                                    '--listen-metrics=:3031'
                                ]
                            }]
                        }
                    }
                }
            }, 
            {
                'apiVersion': 'v1', 
                'kind': 'Secret', 
                'metadata': {
                    'name': 'flux-git-deploy', 
                    'namespace': 
                    'default'
                }, 
                'type': 'Opaque'
            }]
