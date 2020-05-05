# Python custom Kubernetes Operator Demo 
- It's a Demo to handle configmap, which will be be rewritten by operator sdk in the future!
- I would recommend demo-app v2 as the demo, because I remove kubectl sidecar with demo-app v1, which would be more flexible

## demo-app Operator version
- demo-app v2 with sa token
- demo-app v1 with kubectl container

### Build demo-app and demo operator images
```
cd build
docker build -t  docker.io/zhangchl007/demo-app:v1 .

# operator v1
cd ../operator
docker build -t  docker.io/zhangchl007/demo-operator:v1 . -f Dockerfile-v1

cd ../kubectl_img
docker build -t  zhangchl007/k8s-kubectl:v1 .

# operator v2
docker build -t  docker.io/zhangchl007/demo-operator:v2 . -f Dockerfile-v2

```
# Create robot sa to call  the api of kubernetes cluster 
```
kubectl -n kube-system create sa robot
kubectl create -f deploy/robot-clusterrolebindings.yaml
ENDPOINT=192.168.99.108:8443
TOKEN=`kubectl -n kube-system describe $(kubectl -n kube-system get secret -n kube-system -o name | grep robot) |grep token:|tail -1| awk '{print $2}'`
curl -v -k  -H "Authorization: Bearer ${TOKEN}" https://${ENDPOINT}/api/v1/watch/namespaces/default/configmaps\?watch\=true

```
# Deploy demo-app application
```
# deploy demo-app:v2
kubectl create -f deploy/demo-app-crd.yaml
kubectl create -f deploy/demo-app-cr.yaml
kubectl create -f deploy/configmap.yml
kubectl create -f deploy/mysecrets.yaml
kubectl create -f deploy/demo-operator-deploy-v2.yaml

kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
frontend-6f9d59c965-gqhlw   1/1     Running   0          5h56m
operator-5fb795bb-t6w78     1/1     Running   0          3m59s

# deploy demo-app:v1

kubectl create -f deploy/demo-app-crd.yaml
kubectl create -f deploy/demo-app-cr.yaml
kubectl create -f deploy/configmap.yml
kubectl create -f deploy/demo-operator-deploy-v1.yaml
kubectl get pods
NAME                        READY   STATUS    RESTARTS   AGE
frontend-6f9d59c965-gqhlw   1/1     Running   0          5h58m
operator-59995d9856-lbqqf   2/2     Running   0          6s

```
# Watch the status of demo-app endpoint once the configmap had been changed
```
oc get cm -o yaml --export
apiVersion: v1
items:
- apiVersion: v1
  data:
    config.cfg: |
      MSG="Welcome to this demo01!"
      FOO="Welcome to this demo02!"
  kind: ConfigMap

kubectl exec -it frontend-6f9d59c965-5r2ct sh
# curl localhost:5000/hi1
Welcome to this demo02!#
# curl localhost:5000/hi2
Welcome to this demo01!

```
#### Resources 
- Custom kubernetes Operators: https://www.magalix.com/blog/creating-custom-kubernetes-operators
