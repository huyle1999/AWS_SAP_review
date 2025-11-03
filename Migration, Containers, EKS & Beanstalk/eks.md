# 🧠 Lab: Create and Connect to Amazon EKS Cluster

**Region:** us-east-1 (N. Virginia)  
**Duration:** ~60 mins  

---

## 🎯 Goal
Deploy a basic Amazon EKS cluster (`whiz`) and verify connectivity from AWS CloudShell using `kubectl`.  
Understand EKS control plane components, configure kubectl, and validate cluster services.

---

## ⚙️ Steps Summary

### Step 1 — Create EKS Cluster
- **Service:** Elastic Kubernetes Service → *Create Cluster*  
- **Cluster Name:** `whiz`  
- **Kubernetes Version:** default  
- **Cluster IAM Role:** existing role  
- **Node IAM Role:** existing role  
- **Network:** Default VPC, 3 subnets (1a, 1b, 1c)  
- Wait ~10–15 mins until **status = Active**

📸 *Screenshot:* EKS Console showing cluster `whiz` = Active

---

### Step 2 — Setup CloudShell
- Open **CloudShell** and confirm region = `us-east-1`.  
- Install `kubectl`:
  ```bash
  curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amd64/kubectl
  chmod +x ./kubectl
  mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
  kubectl version --short --client
### Step 3 — Connect kubectl to EKS
bash
aws eks update-kubeconfig --region us-east-1 --name whiz
kubectl get svc
✅ Expected Output

NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.100.0.1     <none>        443/TCP   1m
📸 Screenshot: CloudShell terminal showing kubectl get svc

### Step 4 — (Optional) Deploy Test App
bash
Sao chép mã
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --type=LoadBalancer
kubectl get svc nginx -w
✅ Expected: EXTERNAL-IP assigned → open in browser to see Nginx welcome page.

### Step 5 — Clean Up
bash
Sao chép mã
kubectl delete svc nginx
kubectl delete deployment nginx
aws eks delete-cluster --name whiz --region us-east-1
📸 Screenshot: EKS Console after deletion (no clusters listed)

## 🧩 Key Learnings
Amazon EKS manages the control plane; you manage worker nodes and networking.
aws eks update-kubeconfig is required to link kubectl with EKS.
Cluster deletion can take ~10 mins since control plane and node groups are separate.

## 🧰 Troubleshooting Notes
Issue	Root Cause	Fix
kubectl: command not found	PATH missing	Add $HOME/bin to PATH
Unable to connect to server	Wrong region in kubeconfig	Add --region us-east-1
EXTERNAL-IP: <pending>	LoadBalancer not provisioned	Wait or verify default VPC security groups

## 🏁 Resume Line
Deployed and managed Amazon EKS cluster using AWS CloudShell and kubectl, validated connectivity, and deployed a sample Nginx application for testing.