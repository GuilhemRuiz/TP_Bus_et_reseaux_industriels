# Compte rendu du TP Capteurs et réseaux

## Introduction

Ce projet est le résultat de 5 séances de TP fait en dernière année d'école d'ingénieur à l'ENSEA. L’objectif final est de pouvoir récupérer différentes mesures sur une STM32, tel que la température ou la pression grâce au capteur BMP280, de les envoyer vers une Raspberry Pi. Cette dernière pourra afficher les valeurs et l’utilisateur pourra y faire des requêtes telles que demander de nouvelles mesures ou les effacer. Le but des différents TP est de nous faire comprendre le principe et l'utilité de plusieurs bus industriels tels que le CAN, l’I2C et le SPI, ainsi que des liaisons comme l’UART.

## Séance 1 - Bus I2C :

### Capteur BMP280 :

<p align="center">
 <img width="1078" alt="Capture d’écran 2022-10-19 à 08 27 27" src="https://user-images.githubusercontent.com/13495977/197718754-501ed17b-c1ef-42ed-ab40-3fafb46427bc.png">
 Figure 1 : Memory map
</p>

* Il existe deux adresses possibles pour ce composant : 0x76 et 0x77. Cela dépend de où est connecté SDO (sur le GND ou sur VDDIO respectivement). Dans notre cas, nous utiliserons l’adresse 0x77.
* Le registre 0xD0 permet d’identifier ce composant. Sa valeur est 0x58.
* Le registre permettant de placer le composant en mode normal est 0xF4. La Figure 2 ci-dessous nous présente les différents modes de fonctionnements possibles du capteur. Dans notre cas, il faut mettre les deux bits de poids faible à un pour que le capteur soit en mode normal.

<p align="center">
<img width="333" alt="Capture d’écran 2022-10-25 à 10 03 41" src="https://user-images.githubusercontent.com/13495977/197718942-b4600be4-9208-4a67-a0b9-d0f2382a0b53.png"></p>
<p align="center">
Figure 2 : Mode settings
</p>

* Les registres 0x88 à 0xA1 permettent de faire l’étalonnage du capteur. 
* Les registres contenant la température vont de 0xFA à 0xFC. Les données sont sur 20 bits (non-signés), que ce soit pour la température ou pour la pression.
* Les registres contenant la pression vont de 0xF7 à 0xF9.
* La fonction bmp280_compensate_T_int32(BMP280_S32_t adc_T) permet le calcul de la température au format 32 bits.  bmp280_compensate_P_int64(BMP280_S32_t adc_P) permet le calcul de la pression au format 32 bits.


### Trouver l’id du capteur BMP 280 : 

Pour communiquer entre le capteur et la STM32, nous utilisons le protocole I2C. 
Ce protocole communique via deux broches : SDA et SCL. 
Il y a deux modes de communication qui sont l’écriture et la lecture de données. Dans notre cas, nous utiliserons ces deux modes dans le but de récupérer les données de température et de pression du capteur. Pour ce faire, nous avons besoin de l’id du capteur. Cet id est un identifiant qui permet à la carte d’être certaine qu’elle communique avec ce capteur et pas un autre.

Pour récupérer cet identifiant, nous devons suivre un schéma bien précis. Il faut envoyer des données vers le capteur (“écrire”). Ces données sont en réalité une trame de ce type :

<p align="center">
 
Figure 3 : JSP
</p>

Afin de savoir quand commence le message, le signal est mis à 1, puis à 0. L’adresse du composant est présente dans la trame, ici c’est 0x77. Elle est suivie d’un bit à 0 qui indique à la carte qu’on écrit/envoie un message. Ce message est l’adresse de l’id du capteur BMP280. Dans notre cas, on envoie 0xD0 et la carte est censée nous renvoyer 0x58.

Puis, il faut recevoir les données que renvoie le capteur. Il nous renvoie son id. Cette trame :

<p align="center">
 
Figure 4 : JSP
</p>

La trame est sensiblement la même que précédemment, à défaut que le message envoyé par le capteur BMP280 correspond à son ID, c’est-à-dire 0x58. Il est intéressant de noter que le bit d’écriture/lecture est mis à 1, car nous sommes en mode lecture.

On peut aussi noter la présence du type de variable uint8_t à la place d’un int pour déclarer le tableau. Chaque case du tableau fait un octet, contrairement à un int qui en contient deux. Comme l’I2C ne peut envoyer qu’un octet à la fois, il est préférable d’utiliser uint8_t.



## Séance 2 - Raspberry Pi

### Mise en route du raspberry pi Zéro 

Pour configurer le SSID et le mot de passe  du wifi, nous utilisons le logiciel Raspberry Pi Imager. Cependant, pour connecter le port série du GPIO, nous modifions le contenu du fichier config.txt. Nous ajoutons les deux lignes suivantes à la fin du fichier :

<p align="center">

Figure 5 : Fin du fichier config.txt
</p>

Pour que le noyau libère le port UART, nous supprimons la ligne “console=serial0,115200” dans le fichier cmdline.txt.

“Comment la raspberry a obtenu son adresse IP ?” - Avant de commencer, il faut préciser que nous sommes sur un réseau local. Les adresses qui sont distribuées sont donc… locales.
L’équipement qui gère l’attribution de ces adresses est le routeur. En nous connectant à ce dernier, il a attribué une adresse locale à notre Raspberry. Son adresse est : 192.168.88.242/24.

“Comment le savons-nous ?” - Nous avons utilisé le logiciel Angry Ip Scanner qui nous permet d’afficher tous les appareils (et donc adresses IP) présents sur le réseau local. Voici une capture de quelques adresses présentes dessus : 

<p align="center">

Figure 6 : Capture du logiciel Angry Ip Scanner
</p>
 
Dans ce tableau, on retrouve bien notre raspberry pi à l’adresse 192.168.88.242.


### Port Série

#### Loopback

<p align="center">

Figure 7 : Paramètre du minicom
</p>

Dans le minicom, nous avons désactivé le flux matériel (“Hardware Flow Control”) du port série.

#### Communication avec la STM32

Lorsqu’on relie le raspberry et la stm32, il ne faut pas oublier de relier les masses des deux pour avoir une masse commune. C’est préférable de le faire pour deux raisons :

* Premièrement, une masse différente pourrait endommager des composants, car il y a une différence dans la tension de référence (alimentation usb et alimentation ordi portable par exemple).
* Deuxièmement, cette différence de masse peut provoquer des perturbations dans l’envoi et la réception des signaux, car ils ne sont pas sur le même point de référence commun.

Voici à quoi ressemble le système en l’état :

<p align="center">

Figure 8 : Schéma du système actuel
</p>

Ensuite, nous avons testé si la communication entre le Raspberry et la STM32 est bien établie. Nous avons donc uniquement fait communiquer les deux cartes entres-elles :

<p align="center">

Figure 9 : Envoi de la température sur la RPI
</p>

Nous recevons bien les valeurs de température du capteur connecté à la STM32 sur le Raspberry.
La communication entre les deux cartes est donc correcte. Nous pouvons donc essayer d’envoyer des requêtes et voir si nous recevons les valeurs souhaitées.
