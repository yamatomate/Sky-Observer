# Como usar o service de SkyField

Dentro de SkyField tem uma classe chamada `SkyFieldClient` ela faz duas coisas, listar objetos que pode ser observados.

## Inicialização:
Para iniciar a classe precisa passar a latitude e logitude.
```
variavel = SkyFieldClient(latitude=-7.016852, longitude=-42.130789)
```

## Metodos:
- search_object(objeto="Moon", latitude: float = None, longitude: float = None, horario=load.timescale().now() ):
    Atributos do metodo:
    - objeto: pode passar o nome como uma `String` em portugues com a primeira letra maiscula, outro jeito é passando o nome em ingles e por fim por numero
    Retorno do metodo gera `ObjetoVisivelResponse` que possui os seguintes atributos: visible(bool), altitude(float), azimuth(float).
    - `visible` : indica se o objeto está visivel.
    - `altitude` : a altitude de observação.
    - `azimuth` : o azumith de observação.
    
- observable_objects(modo:int=1):
    Atributos do metodo:
    - modo: ao passar 1 receberá os nomes em portugues dos objetos observaveis, já se passar 2 receberá os objetos observaveis no padrão do SkyField permitindo ver o nome em ingles e o numero 

# Exemplos
## Instaciando classe
```
exemplo = SkyFieldClient(latitude=-7.016852, longitude=-42.130789)
```
## search_object
```
exemplo.search_object("Mars", latitude=-7.016852, longitude=-42.130789)
```
retorno:
```
ObjetoVisivelResponse(visible=np.False_, altitude=<Angle -67deg 17' 09.4">, azimuth=<Angle 70deg 39' 28.7)
```
##  observable_objects
```
exemplo.observable_objects()
```
retorno:
```
['Mercúrio', 'Vênus', 'Terra', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno', 'Lua', 'Plutão']
```
