# Projeto de Machine Learning - Estimativa de Frete

## 1. Visão Geral

### O problema
Calcular o frete conforme cotação, considerando que cada transportadora tem suas próprias regras e nenhuma oferece API padronizada.

### A solução proposta
Usar **Machine Learning** para prever o preço do frete com base em 12 anos de dados históricos de notas fiscais.

### Por que funciona?
- **Entrada (features)**: volume, peso, distância, transportadora, região, tipo de produto, etc.
- **Saída (target)**: preço do frete.
- **Volume de dados**: centenas de milhares de notas em 12 anos.

Isso é um problema clássico de **regressão supervisionada**: dado um conjunto de variáveis, prever um valor numérico (o preço do frete).

---

## 2. Dados Necessários

### Estrutura esperada

| id_nota | transportadora | peso_kg | volume_m3 | distancia_km | uf_origem | uf_destino | preco_frete |
|---------|----------------|---------|-----------|--------------|-----------|------------|-------------|
| 1       | Transp A       | 50      | 0.5       | 300          | SP        | MG         | 120.00      |
| 2       | Transp B       | 20      | 0.2       | 150          | SP        | RJ         | 80.00       |
| ...     | ...            | ...     | ...       | ...          | ...       | ...        | ...         |

### Variáveis úteis adicionais
- Data da nota (sazonalidade)
- Tipo de carga
- ICMS
- Cidade origem/destino
- Código do produto

---

## 3. Ferramentas (Python)

| Biblioteca | Uso |
|------------|-----|
| **pandas** | Manipular os dados |
| **scikit-learn** | Treinar modelos simples (Random Forest, Gradient Boosting) |
| **XGBoost** ou **LightGBM** | Modelos mais potentes para dados tabulares |
| **joblib** ou **pickle** | Salvar o modelo treinado |
| **FastAPI** ou **Django** | Criar API para consumir o modelo |

---

## 4. Fluxo do Projeto

```text
[Dados brutos - Notas Fiscais] 
    ↓ (limpeza, feature engineering)
[Dataset limpo]
    ↓ (treino/teste split)
[Treinar modelo]
    ↓ (avaliação: MAE, RMSE, R²)
[Modelo salvo (.pkl)]
    ↓ (deploy)
[API que recebe volume/peso/distância/transportadora e retorna estimativa]
```

---

## 5. Exemplo de Código

### 5.1. Treinar e salvar o modelo

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# 1. Carregar dados
df = pd.read_csv("notas_frete.csv")

# 2. Preparar features e target
features = ["peso_kg", "volume_m3", "distancia_km"]
X = df[features]
y = df["preco_frete"]

# 3. Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Treinar modelo
model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Avaliar
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print(f"Erro médio absoluto: R$ {mae:.2f}")

# 6. Salvar modelo
joblib.dump(model, "modelo_frete.pkl")
```

### 5.2. Usar o modelo para prever

```python
import joblib

model = joblib.load("modelo_frete.pkl")

# Exemplo: peso=30kg, volume=0.3m³, distância=200km
estimativa = model.predict([[30, 0.3, 200]])
print(f"Frete estimado: R$ {estimativa[0]:.2f}")
```

### 5.3. API com FastAPI

```python
from fastapi import FastAPI
import joblib

app = FastAPI()
model = joblib.load("modelo_frete.pkl")

@app.get("/estimar-frete")
def estimar_frete(peso_kg: float, volume_m3: float, distancia_km: float):
    estimativa = model.predict([[peso_kg, volume_m3, distancia_km]])
    return {"frete_estimado": round(estimativa[0], 2)}
```

Rodar:

```bash
uvicorn main:app --reload
```

Acessar:

```
GET http://localhost:8000/estimar-frete?peso_kg=30&volume_m3=0.3&distancia_km=200
```

Retorno:

```json
{"frete_estimado": 95.50}
```

---

## 6. Infraestrutura Necessária

### 6.1. Para desenvolvimento e treino

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8-16 GB |
| **Disco** | 10 GB livres | 50 GB SSD |
| **GPU** | ❌ Não precisa | ❌ Não precisa |
| **SO** | Windows/Linux/Mac | Qualquer |

### 6.2. Para API em produção

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 1 vCPU | 2 vCPUs |
| **RAM** | 1 GB | 2-4 GB |
| **Disco** | 5 GB | 20 GB SSD |
| **GPU** | ❌ Não precisa | ❌ Não precisa |

### 6.3. Opções de VPS baratas

| Provedor | Plano | Specs | Preço |
|----------|-------|-------|-------|
| DigitalOcean | Basic Droplet | 1 vCPU, 1 GB RAM, 25 GB SSD | ~$6/mês |
| Linode | Nanode | 1 vCPU, 1 GB RAM, 25 GB SSD | ~$5/mês |
| Vultr | Cloud Compute | 1 vCPU, 1 GB RAM, 25 GB SSD | ~$5/mês |
| AWS EC2 | t3.micro | 2 vCPU, 1 GB RAM | Free tier / ~$8/mês |
| Azure | B1s | 1 vCPU, 1 GB RAM | ~$7/mês |

### 6.4. Resumo de custos

| Fase | Onde rodar | Custo |
|------|------------|-------|
| Desenvolvimento | Seu PC/notebook | R$ 0 |
| Treino do modelo | Seu PC/notebook | R$ 0 |
| API em produção | VPS simples (1 vCPU, 1-2 GB RAM) | ~R$ 25-50/mês |

---

## 7. Desafios a Considerar

1. **Qualidade dos dados**: dados faltantes, erros, outliers (frete de R$ 0.01 ou R$ 999.999).
2. **Feature engineering**: criar variáveis úteis (ex.: frete por kg, região, sazonalidade).
3. **Modelo por transportadora**: talvez seja melhor treinar um modelo por transportadora, ou usar transportadora como feature categórica.
4. **Atualização**: o modelo precisa ser retreinado periodicamente (novos dados, novas transportadoras, inflação).

---

## 8. Próximos Passos

1. **Extrair os dados** das notas fiscais (SQL Server → CSV ou DataFrame).
2. **Explorar os dados** (pandas, visualizações básicas).
3. **Treinar um modelo simples** (scikit-learn, XGBoost).
4. **Avaliar** (erro médio, R²).
5. **Criar uma API** (FastAPI ou integrar no Django atual).
6. **Deployar** onde preferir.