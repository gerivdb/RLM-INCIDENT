# RLM-INCIDENT Playbook: Triade Fallback

## Informations Générales

| Propriété | Valeur |
|-----------|--------|
| **Incident** | Triade Cognitive - Dégradation/Fallback |
| **Version** | 1.0.0 |
| **Dernière mise à jour** | 2026-07-30 |
| **Composants concernés** | LLUX, PIANO, SPIDX, TRIX, GATEWAY-MANAGER |
| **Contact** | DevOps Team (#infra-alerts) |

---

## Scénarios d'Incident

### 1. LLUX Unhealthy

**Symptômes** :
- `curl http://localhost:47000/health` retourne `unhealthy`
- GATEWAY-MANAGER détecte des échecs de health check

**Actions immédiates** :

```bash
# 1. Vérifier le statut
trix backend status llux

# 2. Voir les logs
tail -f /var/log/trix/llux-*.log

# 3. Redémarrer LLUX
trix backend stop llux
trix backend start llux

# 4. Vérifier la santé
curl http://localhost:47000/health
```

**Fallback** :
```bash
# Basculer vers ollama-env2
kubectl set env deployment/gateway-manager DEFAULT_BACKEND=ollama-env2
```

---

### 2. TRIX Échec de Conteneur

**Symptômes** :
- `trix backend status llux` → `failed`

**Actions immédiates** :

```bash
# 1. Vérifier le WAL
cat /var/lib/trix/wal/llux.log

# 2. Nettoyer le conteneur
trix backend cleanup llux

# 3. Redémarrer
trix backend start llux
```

---

### 3. GATEWAY-MANAGER Router HS

**Actions immédiates** :

```bash
# 1. Redémarrer GATEWAY-MANAGER
systemctl restart gateway-manager

# 2. Recharger la config
curl -X POST http://localhost:9000/admin/reload
```

**Fallback direct** :
```bash
# SKIP GATEWAY
curl -X POST http://localhost:47000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

---

### 4. PIANO Échec d'Orchestration

**Actions immédiates** :

```bash
cd D:/DO/WEB/TOOLS/L4-TOOLS/PIANO
zig build test -- --test-filter llux
zig build -Dcpu=westmere -Drelease-fast
systemctl restart piano
```

---

### 5. SPIDX Embeddings Échouent

**Actions immédiates** :

```bash
zig build test -- --test-filter bpe_tokenizer
cp models/tokenizer.json /opt/trix/models/
trix backend restart llux
```

---

## Procédure de Rollback Complet

```bash
#!/bin/bash
# Rollback complet de la triade

trix backend stop llux
cp /opt/trix/bin/llux.backup /opt/trix/bin/llux
cp /opt/piano/bin/piano.backup /opt/piano/bin/piano
cp /opt/spidx/bin/spidx.backup /opt/spidx/bin/spidx
trix backend start llux
curl http://localhost:47000/health
```

---

## Checklist d'Escalade

| Niveau | Contact | Délai |
|--------|---------|-------|
| **L1** | DevOps On-Call | < 5 min |
| **L2** | SRE Team | < 15 min |
| **L3** | Platform Team | < 30 min |
| **L4** | Architecture Team | < 1h |

---

## Post-Mortem Template

- **Date** : 
- **Incident** : 
- **Durée** : 
- **Impact** : 
- **Cause racine** : 
- **Solution** : 
- **Actions préventives** :