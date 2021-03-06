# -*- coding: utf-8 -*-
"""TP_3_Introducción_a_Aprendizaje_Automático.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10m_0a187YTRsHfpMso-8Swbh7cNgzX18

# Mentoría

## Introduccion al Aprendizaje Automático

### Introducción

En la siguiente notebook se presentará la consigna a seguir para el tercer práctico del proyecto, correspondiente a la materia Introducción al Aprendizaje Automático. El objetivo consiste en explorar la aplicación de diferentes métodos de aprendizaje supervisado aprendidos en el curso, a través de experimentos reproducibles, y evaluando a su vez la conveniencia de uno u otro, así como la selección de diferentes hiperparámetros a partir del cálculo de las métricas pertinentes.

En el caso de nuestro proyecto, nos enfrentamos originalmente a un problema de prediccion. Sin embargo, a los fines de este práctico, lo transformaremos en un problema de clasificación binario, adaptando las el feature objetivo del dataset. Además, será importante evaluar el desbalance de clases y qué decisiones tomaremos al respecto.

Para ello, comenzaremos con las importaciones pertinentes.

### Importaciones
"""

# Commented out IPython magic to ensure Python compatibility.
# Importación de las librerías necesarias
import numpy as np
import pandas as pd
# Puede que nos sirvan también
import matplotlib as mpl
mpl.get_cachedir()
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import sklearn as skl

from sklearn import preprocessing
from sklearn.utils import shuffle
from sklearn.linear_model import LogisticRegression, Perceptron, Ridge
from sklearn.metrics import accuracy_score, confusion_matrix, mean_squared_error, classification_report, roc_curve, auc
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier

from sklearn import metrics

np.random.seed(0)  # Para mayor determinismo

pd.set_option('display.max_columns', 150)
pd.set_option('display.max_rows', 150)
pd.set_option('max_colwidth', 151)

"""## Consigna para Introducción al Aprendizaje Automático

### I. Preprocesamiento

A los fines de realizar este práctico, se utilizará el dataset original.La división entre train y test será realizada en este mismo práctico. A continuación se detallan los pasos a seguir para el preprocesamiento de los datos.

1. Obtención del Dataset

Cargar el conjunto de entrenamiento original.
"""

#Parsing auxiliar
dateparse = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

_ds_energia = pd.read_csv('https://raw.githubusercontent.com/alaain04/diplodatos/master/data/energia_completo.csv')
_ds_energia['hora'] = _ds_energia.Fecha.apply(lambda x: x[11:13])
_ds_energia['Fecha'] = pd.to_datetime(_ds_energia['Fecha'],format='%Y-%m-%d %H:%M:%S')
_ds_energia.head(5)

#Elimino datos del día 3/12/2019 para comenzar un dia completo
_ds_energia.drop(_ds_energia[pd.to_datetime(_ds_energia['Fecha'].dt.date)=='2019-12-03'].index,inplace=True)

#Generamos Period Index y ordenamos el dataset de Energia
_ds_energia.index = pd.PeriodIndex(list(_ds_energia['Fecha']), freq='05T')
_ds_energia = _ds_energia.sort_index()

# _ds_clima
_ds_clima = pd.read_csv('https://raw.githubusercontent.com/alaain04/diplodatos/master/data/clima_posadas_20192020.csv')
_ds_clima['time'] = pd.to_datetime(_ds_clima['time'],format='%Y-%m-%d %H:%M:%S')
#Elegimos features del dataset de Clima y los llevamos cada 5 minutos para poder unirlo con el dataset de energia
_ds_clima.index = pd.PeriodIndex(list(_ds_clima['time']), freq='T')
_ds_clima = _ds_clima[['temperature','windspeed','winddirection']].resample('05T').fillna("backfill")
#Ordenamos valores
_ds_clima = _ds_clima.sort_index()

"""#####Unimos ambos datasets"""

_ds_energia=_ds_energia.join(_ds_clima,how='left')
_ds_energia.head()

"""2. Aplicar Script de Curación

Inicialmente, luego de haber unido ambos datasets, con el objetivo de preparar los datos que alimentarán los modelos de aprendizaje automático (ML) propuestos, deberán aplicar el script de curación obtenido en el práctico anterior. En esta etapa, pueden adicionar los atributos que crean pertinentes a priori o que hayan encontrado interesantes por tener mayor correlación con la variable Target.
"""

#Calculamos los valores absolutos de la Potencia
_ds_energia['abs_Kwatts'] = _ds_energia['Kwatts_3_fases'].abs()

#Calculamos los valores absolutos de la Potencia
_ds_energia['abs_Potencia'] = _ds_energia['Factor_de_Poten_A'].abs()

#Creamos un campo con la fecha del día solamente
_ds_energia['fecha_dia'] = pd.to_datetime(_ds_energia['Fecha'].dt.date) 

_ds_energia['DiaSemana'] = pd.to_datetime(_ds_energia.fecha_dia.dt.date).dt.day_name()
_ds_energia['mes_desc'] = pd.to_datetime(_ds_energia.fecha_dia.dt.date).dt.month_name()

def get_dia_laboral(nombre_dia):
    if nombre_dia in ['Wednesday', 'Thursday', 'Friday', 'Monday','Tuesday']:
        return 'Dia laboral'
    else:
        return 'Fin de semana'

_ds_energia['es_dia_laboral'] = _ds_energia['DiaSemana'].apply(lambda x:get_dia_laboral(x))

# instanciamos clases
le_dia_semana = preprocessing.LabelEncoder()
le_dia_laboral = preprocessing.LabelEncoder()

# Ejecutamos la funcion entrena el modelo de codificación
le_dia_semana.fit(_ds_energia['DiaSemana'])
le_dia_laboral.fit(_ds_energia['es_dia_laboral'])

# View encoder mapping
dict(zip(le_dia_semana.classes_,le_dia_semana.transform(le_dia_semana.classes_)))

dict(zip(le_dia_laboral.classes_,le_dia_laboral.transform(le_dia_laboral.classes_)))

# transfomr -> ejecuta el modelo y retorna el array con los datos transformados

_ds_energia['DiaSemana_Transform'] = le_dia_semana.transform(_ds_energia['DiaSemana']) 
_ds_energia['Es_dia_laboral_Transform'] = le_dia_laboral.transform(_ds_energia['es_dia_laboral'])

# obtengo lista de registros outliers
outl = _ds_energia[_ds_energia.abs_Kwatts > (_ds_energia.abs_Kwatts.median() + 3 * _ds_energia.abs_Kwatts.median())] 
_valor_outlier = _ds_energia.abs_Kwatts.median() + 3 * _ds_energia.abs_Kwatts.median()
print('Límite máximo de consumo para considerar outliers: ' + str(_valor_outlier) )

#Reemplazamos Nan en tensiones
_ds_energia.loc[ ( _ds_energia['Vab'].isna()), 'Vab'] = 0
_ds_energia.loc[ ( _ds_energia['Vca'].isna()), 'Vca'] = 0
_ds_energia.loc[ ( _ds_energia['Vbc'].isna()), 'Vbc'] = 0
#Reemplazamos outliers en tensiones
_ds_energia.loc[ ( _ds_energia['Vab'] > _ds_energia.Vab.median() + 3 * _ds_energia.Vab.median() ), 'Vab'] = 0 #_ds_energia.Vab.median() + 3 * _ds_energia.Vab.median()
_ds_energia.loc[ ( _ds_energia.Vca > _ds_energia.Vca.median() + 3 * _ds_energia.Vca.median() ) , 'Vca'] = 0 #_ds_energia.Vca.median() + 3 * _ds_energia.Vca.median()
_ds_energia.loc[ ( _ds_energia['Vbc'] > _ds_energia.Vbc.median() + 3 * _ds_energia.Vbc.median() ), 'Vbc'] = 0 #_ds_energia.Vbc.median() + 3 * _ds_energia.Vbc.median()

# convertimos los nan de abs_Kwatts en valor 0 si es nan 'Kwatts 3 fases' y 'Amper fase T-A'== 0, luego se marcará como un corte de energia
_ds_energia.loc[ ( _ds_energia['Amper_fase_R_A'].isna()) & (_ds_energia['Amper_fase_T_A'] == 0), 'Amper_fase_R_A'] = 0
_ds_energia.loc[ ( _ds_energia['Amper_fase_S_A'].isna()) & (_ds_energia['Amper_fase_T_A'] == 0), 'Amper_fase_S_A'] = 0
_ds_energia.loc[ ( _ds_energia['Kwatts_3_fases'].isna()) & (_ds_energia['Amper_fase_T_A'] == 0), 'abs_Kwatts'] = 0

#Evaluamos si hubo un corte de energia (o sea, si la potencia total es igual a 0)
_ds_energia.loc[_ds_energia.abs_Kwatts == 0, 'corte_energia'] = 1
_ds_energia.loc[(_ds_energia['Factor_de_Poten_A']<=0) & (_ds_energia['Kwatts_3_fases']>0),
                                               'corte_energia'] = 1
_ds_energia.loc[(_ds_energia['Factor_de_Poten_A']>0) & (_ds_energia['Kwatts_3_fases']<0),
                                               'corte_energia'] = 1                                               

_ds_energia.loc[_ds_energia.abs_Kwatts != 0, 'corte_energia'] = 0

_ds_energia.loc[_ds_energia.Vca == 0, 'corte_energia'] = 1
_ds_energia.loc[_ds_energia.Vab == 0, 'corte_energia'] = 1
_ds_energia.loc[_ds_energia.Vbc == 0, 'corte_energia'] = 1

_ds_energia.loc[_ds_energia['Amper_fase_R_A'] == 0, 'corte_energia'] = 1
_ds_energia.loc[_ds_energia['Amper_fase_T_A'] == 0, 'corte_energia'] = 1
_ds_energia.loc[_ds_energia['Amper_fase_S_A'] == 0, 'corte_energia'] = 1


#Cambiamos outliers sólo en columna nueva
#Evaluamos si hay los outliers de la potencia
_ds_energia.loc[_ds_energia.abs_Kwatts > _valor_outlier, 'outlier_Kwatts'] = 1
_ds_energia.loc[_ds_energia.abs_Kwatts <= _valor_outlier, 'outlier_Kwatts'] = 0


#Decidimos reemplazar los valores outliers de Potencia por 0 ya que consideramos que fue un error de medición y que para poder graficar los datos, necesitamos que no estén.
_ds_energia.loc[_ds_energia['outlier_Kwatts']==1, 'abs_Kwatts'] = 0

_ds_energia.abs_Kwatts.fillna(value=0,inplace=True)
_ds_energia.winddirection.fillna(value=0,inplace=True)
_ds_energia.windspeed.fillna(value=0,inplace=True)

#Verifico Nan
_ds_energia[_ds_energia.abs_Kwatts.isna()==True].abs_Kwatts.count()

"""3. Dataset para Problema de Clasificación Binario

Si bien nuestro problema original implica predecir una variable Real, es decir una regresión, comenzaremos por tratarlo como un problema de clasificación binario, en donde nuestro objetivo será:

- 1 = Hay distribución de energía (Kw 3 fases > 100)
- 0 = No hay distribución de energía  (Kw 3 fases <= 100)

Es decir, queremos diferenciar los momentos en que hay cortes en la distribucion de energia de los que no hay. En base a esta definición, deben transformar el dataset para adaptarlo a un problema de clasifiación binario.
¿Cómo luce ahora el balance de clases? ¿Tomarán alguna decisión al respecto?
"""

#Creamos la columna target seteando un 1 suponiendo que hay energia, para luego evaluar la columna de potencia y asignarle 0 en caso contrario
_ds_energia['target'] = 1
_ds_energia.loc[_ds_energia.abs_Kwatts <= 100, 'target'] = 0
_ds_energia.loc[_ds_energia.corte_energia==1, 'target'] = 0

print('Porcentaje de valor 1 (con distribución de energia) ' + str(_ds_energia[_ds_energia.target==1].Fecha.count()/_ds_energia.Fecha.count()))
print('Porcentaje de valor 0 (sin distribución de energia) ' + str(_ds_energia[_ds_energia.target==0].Fecha.count()/_ds_energia.Fecha.count()))

"""4. *Normalización de Atributos*

Es posible que sea necesario normalizar las features de nuestro dataset, dado que muchos de los algoritmos de clasificación supervisada lo requieren. ¿En qué casos tendrá que implementarse normalización?

Aplicar a los datasets la normalización de atributos que consideren adecuada.
"""

_ds_energia.dtypes

#Funcion para normalizar los campos numéricos de 0 a 1
def normalize(df):
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

dt_normalizado = normalize(_ds_energia.drop(columns=['Kwatts_3_fases','Factor_de_Poten_A','outlier_Kwatts','corte_energia','es_dia_laboral','mes_desc','DiaSemana','fecha_dia','hora','Fecha']))
dt_normalizado.sample(5)

#Funcion para normalizar los campos numéricos de -1 a 1
def normalize_alternativa(df):
    result = df.copy()
    for feature_name in df.columns:
        if feature_name != 'target':
            _mean = df[feature_name].mean()
            _std = df[feature_name].std()
            result[feature_name] = (df[feature_name] - _mean) / (_std)
    return result

dt_normalizado_alternativa = normalize_alternativa(_ds_energia.drop(columns=['Kwatts_3_fases','Factor_de_Poten_A','outlier_Kwatts','corte_energia','es_dia_laboral','mes_desc','DiaSemana','fecha_dia','hora','Fecha']))
dt_normalizado_alternativa.sample(3)

dt_normalizado_alternativa.describe()

# división entre entrenamiento y evaluación
dt_normalizado_alternativa = dt_normalizado_alternativa.dropna()
columns=dt_normalizado_alternativa.columns
X = dt_normalizado_alternativa[columns]
y = dt_normalizado_alternativa.target

"""5. Mezcla Aleatória y División en Train/Test

Finalmente, están en condiciones de dividir el dataset en Train y Test, utilizando para este último conjunto un 20% de los datos disponibles. Previo a esta división, es recomendable que mezclen los datos aleatoriamente. De este modo, deberán obtener cuatro conjuntos de datos, para cada uno de los datasets: X_train, X_test, y_train y y_test.
"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=True)

X_train.shape, y_train.shape

X_test.shape,  y_test.shape

##La proporción cambia al considerar también cortes de energía cuando las tensiones y corrientes están en 0.
##Pasamos de tener una proporción de 90/10 a 53/47
print('Proporción de valor 1 y 0 en el set de training) \n' + str(y_train.value_counts()/y_train.shape[0]) )
print('\nProporción de valor 1 y 0 en el set de testing) \n' + str(y_test.value_counts()/y_test.shape[0]) )

"""6. Division en Train/Test (opcional)

En muchos de los problemas de series temporales la variable objetivo está muy ligada al momento en la cual se la mide. Es por esto que se suele adoptar diferentes estrategias para la división de los dataset de de entrenamiento y test. 

La opción más frecuente es dividirlos en subconjuntos ordenados por el tiempo, de manera que el dataset de entrenamiento sea anterior al de test.

Prueben realizar esta división y ejecutar los mismos modelos para poder comparar resultados sobre las métricas obtenidas.

https://machinelearningmastery.com/backtest-machine-learning-models-time-series-forecasting/


A modo de ayuda, en esta notebook encontrarán una especie de template que sigue los pasos propuestos y que deberán ir completando.

Recuerden que la ciencia de datos es un proceso circular, continuo y no lineal. Es decir, si los datos requieren de mayor procesamiento para satisfacer las necesidades de algoritmos de ML (cualesquiera de ellos), vamos a volver a la etapa inicial para, por ejemplo, crear nuevas features, tomar decisiones diferentes sobre valores faltantes o valores atípicos (outliers), descartar features, entre otras.

### II. Aplicación de Modelos de Clasificación

Una vez finalizada la etapa de preprocesamiento, se propone implementar diferentes modelos de clasificación para ambos datasets, utilizando la librería Scikit-Learn:

    Perceptron. Utilizar el método Stochastic Gradient Descent (Recuerden mezclar aleatoriamente los datos antes de cada iteración)
    K Nearest Neighbors ó K Vecinos Más Cercanos
    Regresión Logística. Utilizar el método Stochastic Gradient Descent (Recuerden mezclar aleatoriamente los datos antes de cada iteración)

Para cada uno de ellos, se pide responder las siguientes consignas:

    Utilizar dos features para graficar las clases y la frontera de decisión, siempre que sea posible.
    Agregar vector de Bias, cuando lo crean pertinente. Cuándo hace falta y cuándo no? Por qué?
    Obtener accuracy o exactitud.

De estos tres tipos de modelos, cuál creen que es el más adecuado para nuestro caso de aplicación?

Elegir el modelo que consideren que mejor aplica a nuestro problema. Para ello, recuerden que los pasos a seguir en la selección pueden esquematizarse como sigue:
1. Descripción de la Hipótesis

¿Cuál es nuestro problema? ¿Cómo se caracteriza? ¿Cuál es la hipótesis?

**El problema esta enfocado en determinar si el servicio de distribución de energía se encuentra activo o cortado.  El valor a predecir es de tipo binario donde el valor 1 corresponde a servicio activo y el valor 0 indica que hubo un corte.**

2. Selección de Regularizador

¿Utilizarán algún regularizador?¿Cuál?

**Si bien no seleccionamos ningún regulizador fijo, con la selección de los mejores hiperparámetros se termina utilizando el regulador L1.**

3. Selección de Función de Costo

¿Cuál será la función de costo utilizada?

**Para la regresión logística utilizando la logarítmica o sigmoide y para Perceptrón, su función homónima.**

4. Justificación de las Selecciones

¿Por qué eligieron el modelo, el regularizador y la función de costo previas?

**Para el tipo de problema binario, los modelos que mejores se adaptan son la regresión logística y el perceptrón.**

Finalmente, para el modelo selecionado:

    Utilizar el método Grid Search, o de búsqueda exahustiva, con cross-validation para profundizar en la búsqueda y selección de hiperparámetros.
    Calcular métricas sobre el conjunto de entrenamiento y de evaluación para los mejores parámetros obtenidos:
        Accuracy o exactitud
        Reporte de clasificación
        Confusion matrix o matriz de confusión (graficar como heatmap)
        Curva ROC y área bajo la curva (AUC).

**Verifico la correlacion de las varibles para seleccionar 2 que no tengan mucho correlacion**
"""

# división entre entrenamiento y evaluación
dt_normalizado = dt_normalizado.dropna()

X = dt_normalizado.iloc[:, dt_normalizado.columns != 'target']
y = dt_normalizado.target

# división entre entrenamiento y evaluación
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=True)

display(X_train.shape, y_train.shape)
display(X_test.shape,  y_test.shape)

print('Proporción de valor 1 y 0 en el set de training) \n' + str(y_train.value_counts()/y_train.shape[0]) )
print('\nProporción de valor 1 y 0 en el set de testing) \n' + str(y_test.value_counts()/y_test.shape[0]) )

#Matriz de correlación
plt.figure(figsize=(10,10))
sns.heatmap(X_train.corr(), annot=True)

X_train = X_train[['abs_Kwatts',  'temperature']]
X_test = X_test[['abs_Kwatts',  'temperature']]

#Modelos con valores default
_cant_grupos = 10


model_perceptron = SGDClassifier(random_state=0, loss='perceptron')
model_reg_log = SGDClassifier(random_state=0, loss='log')
model_kn = KNeighborsClassifier(n_neighbors = _cant_grupos)

model_perceptron.fit(X_train, y_train)
model_reg_log.fit(X_train, y_train)
model_kn.fit(X_train, y_train)

y_train_pred_perceptron = model_perceptron.predict(X_train)
y_train_pred_reg_log = model_reg_log.predict(X_train)
y_train_pred_kn = model_kn.predict(X_train)

y_pred_perceptron = model_perceptron.predict(X_test)
y_pred_reg_log = model_reg_log.predict(X_test)
y_pred_kn = model_kn.predict(X_test)

#Accuracy o exactitud
#Reporte de clasificación
#Confusion matrix o matriz de confusión (graficar como heatmap)
#Curva ROC y área bajo la curva (AUC).

print(f"Accuracy Perceptron: Train {accuracy_score(y_train, y_train_pred_perceptron)} - Test {accuracy_score(y_test, y_pred_perceptron)}")
print(f"Accuracy Reg Logistica: Train {accuracy_score(y_train, y_train_pred_reg_log)} - Test {accuracy_score(y_test, y_pred_reg_log)}")
print(f"Accuracy K Vecinos: Train {accuracy_score(y_train, y_train_pred_kn)} - Test {accuracy_score(y_test, y_pred_kn)}")

print("Reporte clasificacion test PERCEPTRON")
print(classification_report(y_test, y_pred_perceptron))

print("Reporte clasificacion test REG LOGISTICA")
print(classification_report(y_test, y_pred_reg_log))

print("Reporte clasificacion test KN VECINOS")
print(classification_report(y_test, y_pred_kn))

print("Matriz de confución PERCEPTRON")
cm =confusion_matrix(y_test, y_pred_perceptron)
display(cm)

print("Matriz de confución REG LOGISTICA")
cm =confusion_matrix(y_test, y_pred_reg_log)
display(cm)

print("Matriz de confución KN VECINOS")
cm =confusion_matrix(y_test, y_pred_kn)
display(cm)

#curva roc/auc

metrics.plot_roc_curve(model_perceptron, X_test, y_test) 
metrics.plot_roc_curve(model_reg_log, X_test, y_test) 
metrics.plot_roc_curve(model_kn, X_test, y_test)
plt.show()

#Modelos con busqueda de hiperparametros

param_grid = {
    'loss': ['hinge', 'log','squared_hinge'],
    'penalty': ['l2', 'l1',],
    'alpha': [.00001,.0001, .001],
    'learning_rate': ['constant','optimal','adaptive'],
    'eta0':[.0001],
}

model = SGDClassifier(random_state=0,shuffle=True)
model_gscv = GridSearchCV(model,param_grid,scoring='precision',cv=5)

model_gscv.fit(X_train, y_train)

display(model_gscv.best_estimator_)
display(model_gscv.best_params_)

print(model_gscv.best_estimator_.score(X_train, y_train))
y_pred_hiperparametros = model_gscv.best_estimator_.predict(X_test)

print(f"Accuracy hiperparametro: Train {accuracy_score(y_train, y_train)} - Test {accuracy_score(y_test, y_pred_hiperparametros)}")

print("Reporte clasificacion test HIPERPARAMETROS")
print(classification_report(y_test, y_pred_hiperparametros))

print("Matriz de confución HIPERPARAMETROS")
cm =confusion_matrix(y_test, y_pred_hiperparametros)
display(cm)

#Modelos con busqueda de hiperparametros para KNeighborsClassifier
_cant_grupos = list(range(6,10))

param_grid = {
    'n_neighbors': _cant_grupos,
    'weights': ['uniform', 'distance'],
    'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
    'p': [1,2]
}

model_KN = KNeighborsClassifier()
model_gscv_KN = GridSearchCV(model_KN,param_grid,scoring='precision',cv=5)

model_gscv_KN.fit(X_train, y_train)

display(model_gscv_KN.best_estimator_)
display(model_gscv_KN.best_params_)

y_pred_KN_hiperparametros = model_gscv_KN.best_estimator_.predict(X_test)

print(f"Accuracy hiperparametro KN: Train {accuracy_score(y_train, y_train)} - Test {accuracy_score(y_test, y_pred_KN_hiperparametros)}")

print("Reporte clasificacion test KN HIPERPARAMETROS")
print(classification_report(y_test, y_pred_KN_hiperparametros))

print("Matriz de confusión KN HIPERPARAMETROS")
cm =confusion_matrix(y_test, y_pred_KN_hiperparametros)
display(cm)

metrics.plot_roc_curve(model_gscv_KN.best_estimator_, X_test, y_test)

#Graficamos Límites de Decisión de Perceptrón
from yellowbrick.contrib.classifier import DecisionViz 
viz = DecisionViz(
    model_gscv.best_estimator_, title="Linear SVM",
    features=['Feature One', 'Feature Two'], classes=['A', 'B']
)
viz.fit(X_train.to_numpy(), y_train)
viz.draw(X_test.to_numpy(), y_test)

#Graficamos Límites de Decisión de Regresión Logística
viz = DecisionViz(
    model_reg_log, title="Linear SVM",
    features=['Feature One', 'Feature Two'], classes=['A', 'B']
)
viz.fit(X_train.to_numpy(), y_train)
viz.draw(X_test.to_numpy(), y_test)

#Graficamos Límites de Decisión de KN
viz = DecisionViz(
    model_gscv_KN.best_estimator_, title="Nearest Neighbors",
    features=['Feature One', 'Feature Two'], classes=['A', 'B']
)
viz.fit(X_train.to_numpy(), y_train)
viz.draw(X_test.to_numpy(), y_test)

"""## Entregables

El entregable de este práctico consiste en esta misma Notebook, pero con el preprocesamiento aplicado y los modelos implementados, agregando las explicaciones que crean pertinentes y las decisiones tomadas, en caso de corresponder.
"""

