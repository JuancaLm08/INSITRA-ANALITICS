     # U T I L I I D A D E S
import pandas as pd

#  C O N S T U C C I O N      D E      D A T O S
#Pasajeros por unidad y día.
def construir_pud(
        ps: pd.DataFrame,
):  
#Renombra la columnas del dataset
    ps  = ps.rename(columns={
        'terid': 'Unidad',
        'on': 'Ascensos',
        'off': 'Descensos',
        'opentime': 'Apertura de puerta',
        'closetime': 'Cierre de puerta',
        'lat': 'Latitud',
        'lng': 'Longitud',
    })
    
    #transforma a datetimes
    ps['Apertura de puerta'] = pd.to_datetime(ps['Apertura de puerta'], format="%Y-%m-%d %H:%M:%S")
    ps['Cierre de puerta'] = pd.to_datetime(ps['Cierre de puerta'], format="%Y-%m-%d %H:%M:%S")

    #Construimos el dataset.
    return (ps.groupby([ps['Apertura de puerta'].dt.date, 'Unidad'])[['Ascensos','Descensos']]
        .sum().reset_index())


#Kilometros por unidad y dia.
def construir_kud(
        km: pd.DataFrame,
):
    # Renombra la columnas del dataset
    km = km.rename(columns={
        'terid': 'Unidad',
        'mileage': 'Kilometraje',
        'starttime': 'Dia inicio',
        'endtime': 'Tiempo final',
    })

    # Asegura tipos correctos y tolera formatos inesperados
    km['Dia inicio']   = pd.to_datetime(km['Dia inicio'], errors='coerce')               
    km['Tiempo final'] = pd.to_datetime(km['Tiempo final'], errors='coerce')             
    km['Kilometraje']  = pd.to_numeric(km.get('Kilometraje'), errors='coerce')           

    # Limpia las fechas con la columna inválida
    km = km.dropna(subset=['Dia inicio'])

    # Deja 'Dia inicio' como date puro (para que compare bien con el input en el front end)
    km = km.assign(**{'Dia inicio': km['Dia inicio'].dt.date})

    # Construimos el dataset agrupado
    return (
        km.groupby(['Dia inicio', 'Unidad'], as_index=False)['Kilometraje']
          .sum()
          .sort_values(['Dia inicio', 'Unidad'])
    )
    
        


     

