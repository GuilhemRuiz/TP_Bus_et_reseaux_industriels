# Compte rendu du TP Capteurs et réseaux

## Introduction

<p align ="justify">Ce projet est le résultat de 5 séances de TP fait en dernière année d'école d'ingénieur à l'ENSEA. L’objectif final est de pouvoir récupérer différentes mesures sur une STM32, tel que la température ou la pression grâce au capteur BMP280, de les envoyer vers une Raspberry Pi, ainsi que de faire fonctionner un moteur à pas. La Raspberry Pi pourra afficher les valeurs et l’utilisateur pourra y faire des requêtes telles que demander de nouvelles mesures ou les effacer. Le but des différents TP est de nous faire comprendre le principe et l'utilité de plusieurs bus industriels tels que le CAN, l’I2C et le SPI, ainsi que des liaisons comme l’UART.</p>

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
Figure 2 : Réglages mémoire
</p>

* Les registres 0x88 à 0xA1 permettent de faire l’étalonnage du capteur. 
* Les registres contenant la température vont de 0xFA à 0xFC. Les données sont sur 20 bits (non-signés), que ce soit pour la température ou pour la pression.
* Les registres contenant la pression vont de 0xF7 à 0xF9.
* La fonction `bmp280_compensate_T_int32(BMP280_S32_t adc_T)` permet le calcul de la température au format 32 bits.  `bmp280_compensate_P_int64(BMP280_S32_t adc_P)` permet le calcul de la pression au format 32 bits.


### Trouver l’id du capteur BMP 280 : 

<p align ="justify">Pour communiquer entre le capteur et la STM32, nous utilisons le protocole I2C. 
Ce protocole communique via deux broches : SDA et SCL. 
Il y a deux modes de communication qui sont l’écriture et la lecture de données. Dans notre cas, nous utiliserons ces deux modes dans le but de récupérer les données de température et de pression du capteur. Pour ce faire, nous avons besoin de l’id du capteur. Cet id est un identifiant qui permet à la carte d’être certaine qu’elle communique avec ce capteur et pas un autre.

Pour récupérer cet identifiant, nous devons suivre un schéma bien précis. Il faut envoyer des données vers le capteur (“écrire”). Ces données sont en réalité une trame de ce type :</p>

<p align="center">
<img width="333" alt="boDessinWrite1" src="https://user-images.githubusercontent.com/114395436/202483787-9f77bcc1-964a-4933-81b6-f7e9b49e32cb.png">
</p>
<p align="center">
Figure 3 : Écriture de trame
</p>

<p align ="justify">Afin de savoir quand commence le message, le signal est mis à 1, puis à 0. L’adresse du composant est présente dans la trame, ici c’est 0x77. Elle est suivie d’un bit à 0 qui indique à la carte qu’on écrit/envoie un message. Ce message est l’adresse de l’id du capteur BMP280. Dans notre cas, on envoie 0xD0 et la carte est censée nous renvoyer 0x58.

Puis, il faut recevoir les données que renvoie le capteur. Il nous renvoie son id. Cette trame :</p>

<p align="center">
<img width="333" alt="boDessinWrite2" src="https://user-images.githubusercontent.com/114395436/202483570-b0921605-6999-439e-8641-d4063d8e3a7b.png">
</p>
<p align="center">
Figure 4 : Lecture de trame
</p>

<p align ="justify">La trame est sensiblement la même que précédemment, à défaut que le message envoyé par le capteur BMP280 correspond à son ID, c’est-à-dire 0x58. Il est intéressant de noter que le bit d’écriture/lecture est mis à 1, car nous sommes en mode lecture.

On peut aussi noter la présence du type de variable `uint8_t` à la place d’un int pour déclarer le tableau. Chaque case du tableau fait un octet, contrairement à un int qui en contient deux. Comme l’I2C ne peut envoyer qu’un octet à la fois, il est préférable d’utiliser `uint8_t`.</p>



## Séance 2 - Raspberry Pi

### Mise en route du raspberry pi Zéro 

<p align ="justify">Pour configurer le SSID et le mot de passe  du wifi, nous utilisons le logiciel Raspberry Pi Imager. Cependant, pour connecter le port série du GPIO, nous modifions le contenu du fichier config.txt. Nous ajoutons les deux lignes suivantes à la fin du fichier :</p>

```
enable_uart=1
dtoverlay=disable-bt
```
Pour que le noyau libère le port UART, nous supprimons la ligne “console=serial0,115200” dans le fichier cmdline.txt.

“Comment la raspberry a obtenu son adresse IP ?” - Avant de commencer, il faut préciser que nous sommes sur un réseau local. Les adresses qui sont distribuées sont donc… locales.
L’équipement qui gère l’attribution de ces adresses est le routeur. En nous connectant à ce dernier, il a attribué une adresse locale à notre Raspberry. Son adresse est : 192.168.88.242/24.

“Comment le savons-nous ?” - Nous avons utilisé le logiciel Angry Ip Scanner qui nous permet d’afficher tous les appareils (et donc adresses IP) présents sur le réseau local. Voici une capture de quelques adresses présentes dessus : 

<p align="center">
<img width="333" alt="angryIp" src="https://user-images.githubusercontent.com/114395436/202483086-78ad399c-f4c5-4796-bde3-e28e3fceb7a7.png">
</p>
<p align="center">
Figure 6 : Capture du logiciel Angry Ip Scanner
</p>
 
<p align ="justify">Dans ce tableau, on retrouve bien notre raspberry pi à l’adresse 192.168.88.242.</p>


### Port Série

#### Loopback

<p align="center">
 <img width="333" alt="paramMinicom" src="https://user-images.githubusercontent.com/114395436/202482958-b989a22f-5f5e-4eac-b8a2-af6864169e1f.png">
</p>
<p align="center">
 Figure 7 : Paramètre du minicom
</p>

<p align ="justify">Dans le minicom, nous avons désactivé le flux matériel (“Hardware Flow Control”) du port série.</p>

#### Communication avec la STM32

<p align ="justify">Lorsqu’on relie la Raspberry et la STM32, il ne faut pas oublier de relier les masses des deux pour avoir une masse commune. C’est préférable de le faire pour deux raisons :</p>

* Premièrement, une masse différente pourrait endommager des composants, car il y a une différence dans la tension de référence (alimentation USB et alimentation ordi portable par exemple).
* Deuxièmement, cette différence de masse peut provoquer des perturbations dans l’envoi et la réception des signaux, car ils ne sont pas sur le même point de référence commun.

<p align ="justify">Voici à quoi ressemble le système en l’état :</p>

<p align="center">
 <img width="333" alt="boDessin" src="https://user-images.githubusercontent.com/114395436/202482802-a27f1afb-e03b-4bc5-a1d6-545db078ad78.png">
</p>
<p align="center">
 Figure 8 : Schéma du système actuel
</p>

<p align ="justify">Ensuite, nous avons testé si la communication entre le Raspberry et la STM32 est bien établie. Nous avons donc uniquement fait communiquer les deux cartes entres-elles :</p>

<p align="center">
 <img width="333" alt="putty1250" src="https://user-images.githubusercontent.com/114395436/202482557-d067802d-9c0b-434e-9fde-da28bb15ee79.png">
</p>
<p align="center">
 Figure 9 : Envoi de la température sur la RPI
</p>

<p align ="justify">Nous recevons bien les valeurs de température du capteur connecté à la STM32 sur le Raspberry.
La communication entre les deux cartes est donc correcte. Nous pouvons donc essayer d’envoyer des requêtes et voir si nous recevons les valeurs souhaitées.</p>

## Séance 3 - API REST

### Installation 
<p align ="justify">Après avoir créé un nouvel utilisateur sur la RPI, on lui affecte différents droits, ici celui d’utiliser le port série et celui d’utiliser les commandes super utilisateur.
Le fait d’affecter à la main chaque droit de chaque nouvel utilisateur permet de limiter la casse en cas de piratage. Par exemple, dans le cas où ce nouvel utilisateur se fait pirater, le hackeur n’aura que le droit d’accès au port série et le droit d’utiliser des commandes super utilisateur (mais il faudra alors un autre mot de passe). 
Créons maintenant un serveur web. Pour cela nous allons utiliser le framework Flask.</p>

```pi@raspberrypi:~/server $ FLASK_APP=hello.py FLASK_ENV=development flask run --host 0.0.0.0```

<p align ="justify">Cette commande nous permet de sortir de la loopback. C’est-à-dire, qu’avant cette commande, nous ne restons que sur le terminal.  Après cette commande, nous pouvons afficher notre « Hello World ! » sur notre serveur web sur le même réseau local.
Pour vérifier si le programme fonctionne correctement, il suffit de rentrer l’adresse IP du Raspberry et son port (192.168.88.242:5000) sur notre navigateur favori.
« Host 0.0.0.0 » explique à notre Raspberry qu’on lance le serveur web à l’adresse actuelle, donc 192.168.88.242.
On lance le serveur web avec l’url suivante :</p>

<p align="center">
<img width="679" alt="Capture d’écran 2022-11-17 à 16 28 10" src="https://user-images.githubusercontent.com/13495977/202487969-76949d53-7eed-4063-81a4-618199fd7a49.png">
</p>
<p align="center">
Figure 10 : URL de notre site web
</p>

<p align ="justify">Et on reçoit cette réponse :</p>

<p align="center">
 <img width="727" alt="Capture d’écran 2022-11-17 à 16 30 53" src="https://user-images.githubusercontent.com/13495977/202488545-37534af4-2450-479e-87b3-38bb208a289c.png">
</p>
<p align="center">
Figure 11 : Message d'erreur du site web
</p>

<p align ="justify">Lorsqu’on rajoute la ligne de code suivante et qu’on utilise l’aide F12 sur chrome, on peut observer les tentatives de connexions au serveur web. </p>

<p align="center">
<img width="693" alt="Capture d’écran 2022-11-17 à 16 37 47" src="https://user-images.githubusercontent.com/13495977/202490418-56bc4f25-cdae-406b-9883-d848e92f5136.png">
</p>
<p align="center">
<img width="751" alt="Capture d’écran 2022-11-17 à 16 38 08" src="https://user-images.githubusercontent.com/13495977/202490444-a56be215-2727-4974-bc20-d5e052c53afe.png">
</p>
<p align="center">
Figure 12 et 13 : JSP
</p>

<p align ="justify">Contrairement à notre première tentative, on remarque que le serveur a répondu et que le contenu sur le serveur web a été téléchargé. La connexion est établie.

Si on ajoute ce bout de code :</p>

```Python
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
```

<p align ="justify">La page d’erreur change et donne :</p>


<p align="center">
 <img width="757" alt="Capture d’écran 2022-11-17 à 16 42 47" src="https://user-images.githubusercontent.com/13495977/202491431-b7e4c1a7-17df-4811-8309-28b29ca4f9da.png">
</p>
<p align="center">
Figure 14 : Problème d'affichage du template
</p>

<p align ="justify">Nous avons ajouté une condition dans le code qui renvoie une erreur 404 lorsque l’index dépasse l’index maximal du texte « Welcome to 3ESE API! » et qui nous renvoie l’index et la valeur de ce dernier dans le cas contraire.
Voici un exemple :</p>

<p align="center">
 <img width="754" alt="Capture d’écran 2022-11-17 à 16 45 18" src="https://user-images.githubusercontent.com/13495977/202492104-fa515f67-7ac3-47e1-84ee-477432758b0c.png">
</p>
<p align="center">
Figure 15 : Nouvelle URL
</p>

Dans ce cas, l’index est 19. On reçoit ce message sur le serveur web :

```
{"index": 19, "val": "!", "indexMax":20}
```

L’index sélectionné est bien le 19, la valeur est « ! » et on se rappelle que l’indexMax est 20.
Si on fixe la valeur de l’index à 20, on obtient ce message :

<p align="center">
 <img width="716" alt="Capture d’écran 2022-11-17 à 16 49 04" src="https://user-images.githubusercontent.com/13495977/202493040-284ba5ee-38cf-4986-9851-b1ece027515d.png">
</p>
<p align="center">
Figure 15 : Autre message d'erreur 404
</p>

C’est normal, on indique à l’utilisateur que ça requête n’est pas la bonne. Il a dépassé le seuil de l’index.

```
curl -X POST http://192.168.88.242:5001/api/welcome/14
```

<p align ="justify">La commande ci-dessus ne fonctionne pas. C’est tout à fait normal puisque l’on essaye de faire un POST et que nous ne l’avons pas autorisé. Le serveur nous renvoie donc la bonne erreur : erreur 405 : méthode non autorisée. En remplaçant le post par un get dans la commande, on peut résoudre le problème et le serveur nous renvoie bien quelque chose.</p>

<p align="center">
 <img width="750" alt="Capture d’écran 2022-11-17 à 16 50 57" src="https://user-images.githubusercontent.com/13495977/202493529-0e830be4-2b30-4133-a9d8-64d8873fe0a3.png">
</p>
<p align="center">
Figure 16 : Requêtes GET et POST
</p>

# Séance 4 

Le but de la séance est d’envoyer des commandes par protocole CAN à un moteur afin de le piloter. Nous utilisons pour ce faire une carte STM32 nucléo ainsi qu’un shield pour le CAN. 

Pour le code, il nous faut utiliser les primitives HAL. L’une d’entre elle, la HAL_CAN_AddTxMessage nécéssite certains paramètres pour fonctionner, notamment pHeader, une structure comprenant les champs suivants :
* `.StdId` contient le message ID quand celui-ci est standard (11 bits)
* `.ExtId` contient le message ID quand celui-ci est étendu (29 bits) 
* `.IDE` définit si la trame est standard (CAN_ID_STD) ou étendue (CAN_ID_EXT)
* `.RTR` définit si la trame est du type standard (CAN_RTR_DATA) ou RTR (CAN_RTR_REMOTE) (voir le cours)
* `.DLC` entier représentant la taille des données à transmettre (entre 0 et 8)
* `.TransmitGlobal` dispositif permettant de mesurer les temps de réponse du bus CAN, qu'on utilisera pas. Le fixer à DISABLE
Dans notre cas, nous voulons envoyer un message standard, donc `.ExtId` est mis à 0. Pour `.StdId` nous l’avons mis à 0x60. La Figure 17 ci-après nous montre les différentes valeurs que peut contenir le `.StdId`. 

<p align="center">
<img width="1099" alt="Capture d’écran 2022-11-15 à 22 12 56" src="https://user-images.githubusercontent.com/13495977/202691153-ee48334e-6ada-47af-bda0-88a720bd239c.png">
</p>
<p align="center">
Figure 17 : Les différents modes de fonctionnement du moteur
</p>

Nous avons choisi de nous mettre en mode manuel. Il nous faut donc 3 valeurs : D0 (correspondant au sens de rotation) que nous avons mis à 0, D1 (correspondant à l’angle parcouru par le moteur à chaque itération) que nous avons mis à 0x2D (pour avoir 45°) et enfin D2 (correspondant à la vitesse de rotation) que nous avons mis à la valeur maximum : 0xFF.
Cependant, notre moteur ne tourne pas. Nous ne comprenons pas d’où provient l’erreur. Le code semble correct et l’électronique est bonne. 
Pour comprendre ce qui se passe, nous utilisons un oscilloscope qui va nous permettre de déterminer si nous envoyons des données. Il s’avère que ce n’est pas le cas. On vérifie le câblage du shield sur la Nucleo. Tout est bien branché, il n’y a pas de faux contacts, c’est le software qui est fautif. Malheureusement, nous ne pouvons plus continuer, la séance de TP touche à sa fin.
Cependant, nous avons retiré une inconnue et nous avons déterminé que c’était la partie logicielle qui était responsable du bug.

## Séance 5 - Mise en commun des TP précédents

### Introduction au TP

<p align ="justify">Le but de ce TP est de mettre en commun les TP précédents afin que tout fonctionne en même temps. Plus précisément, l’objectif est retravailler sur l’API REST afin qu’elle puisse envoyer de nouvelles commandes (cf. Figure 17), notamment acquérir les données des capteurs et des moteurs. On pourra aussi modifier certaines valeurs comme celles des moteurs par exemple.</p>

<p align="center">
 <img width="757" alt="cmdApiRest" src="https://user-images.githubusercontent.com/13495977/202491431-b7e4c1a7-17df-4811-8309-28b29ca4f9da.png">
</p>
<p align="center">Figure 18 - Nouvelles commandes de l'API REST</p>

### Réception et transmission - Trame du bus CAN

<p align ="justify">Lors du TP précédent, nous avons eu des problèmes avec le moteur. Après avoir revu le cablage, la carte, le shield et le code nous avons pu résoudre notre problème. Ce dernier venait en effet de la programmation. Une fois résolu nous pouvons passer à la mise en commun des TP.
Nous vérifions que la trame du bus CAN soit bien reçue par le moteur grâce à l’oscilloscope. C’est le cas. Contrairement à la dernière séance, nous n’avons plus une simple ligne droite, mais une vraie trame.</p>

<p align="center">
 <img width="757" alt="trameBusCAN" src="https://user-images.githubusercontent.com/13495977/202491431-b7e4c1a7-17df-4811-8309-28b29ca4f9da.png">
</p>
<p align="center">Figure 19 - Trame Bus CAN</p>

<p align ="justify">Comme nous manquons de temps, nous nous concentrons sur le capteur et sur les commandes de l’API liées. Nous étoffons donc notre code Python avec une nouvelle fonction :</p>

```Python
@app.route('/api/request/temp/', methods=['GET', 'POST'])
def request_temp():
        if request.method == 'GET':
                ser = serial.Serial('/dev/ttyAMA0')
                ser.baudrate = 115200
                ser.close()   
                ser.open()
                ser.write(5)
                test = ser.write(5)
                print(test)
                temp = ser.read()
                insererValTab(temp)
                return temp, 205
```

<p align ="justify">Cette fonction permet d’envoyer le chiffre 5 par UART et de lire les caractères reçus par la suite. Cette dernière permet aussi de stocker les valeurs reçues dans une base de données.

Nous codons juste après le fichier main.c ci-dessous qui nous permet, à la réception de la valeur 5, d’aller demander au capteur la température et la renvoyer à la RPI, toujours en utilisant l’UART.</p>

```C
while (1)
{
 if(HAL_UART_Receive(&huart3, *pData, 1, 10000) == 5){
   BMP280_get_temperature();
   int tempRecup = BMP280_get_temperature();
   HAL_UART_Transmit(&huart3, tempRecup, 1, 10000);
 }
 HAL_Delay(1000);
 ```

<p align ="justify">Cependant, cela ne fonctionne pas. Nous sommes certains que le capteur de température et de pression fonctionne. Nous arrivons à récupérer ses valeurs en hexadécimal, comme en témoigne cette capture ci-dessous :</p>


<p align="center">
 <img width="150" alt="valCaptTempPression" src="https://user-images.githubusercontent.com/114395436/202497538-a7f2b236-3802-4c6b-9d19-e663563d64a0.png">
</p>
<p align="center">Fig 20 - Valeurs du capteur de température et de pression en hexa</p>

<p align ="justify">Le problème ne vient donc pas de la fonction BMP280_get_temperature(). Nous avons sans doute mal codé la récupération des requêtes envoyées depuis la RPI.
Nous n’avons plus assez de temps et c’est dommage, car nous ne sommes pas loin de faire communiquer la Raspberry Pi avec la nucleo pour faire fonctionner le moteur.</p>
