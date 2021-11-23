import math
from operator import itemgetter

# Primero creamos nuestra clase Proceso donde definimos las variables que son parte de un proceso
# Aqui mismo hicimos los metodos para que la obtención de estas variables sea mucho mas facil
# Al mismo tiempo se hicieron las formulas para sacar todos los tiempos (TVC, TB, TT, TF)
# Al final hicimos un metodo __str__ para que los objetos que tenemos guardados como procesos sean faciles de leer 

class Proceso:
    def __init__(self, tdisponible, nombre_proceso, tejecucion, cbloqueo):
        self.tinicio = tdisponible
        self.nombre = nombre_proceso
        self.tduracion = tejecucion
        self.tc = 0 
        self.tb = 0 
        self.tvc = 0 
        self.tt = 0 
        self.ti = 0 
        self.tf = 0 
        self._cbloqueo = cbloqueo
    
    def getinicio(self):
        return self.tinicio

    def getname(self):
        return self.nombre

    def gettt(self):
        return self.tt

    def tiempos(self, tinicial, tiempo_c_c, quantum, tbloqueo, tcmicro):
        self.ti = tinicial
        self.tc = tiempo_c_c
        self.calculoTVC(quantum, tcmicro)
        self.calculoTB(tbloqueo)
        self.calculoTT()
        self.calculoTF()

    def calculoTVC(self, quantum, tc):
        self.tvc = (math.ceil(self.tduracion/quantum)-1)*tc
    
    def calculoTT(self):
        self.tt = self.tc + self.tb + self.tduracion + self.tvc

    def calculoTB(self, tbloqueo):
        self.tb = tbloqueo * self._cbloqueo
    
    def calculoTF(self):
        self.tf = self.ti + self.tt

    def __repr__(self):
        datos = "\nProceso: {proceso:<6}| TCC: {TCC:^5}| TE: {TE:^5}| TVC: {TVC:^5}| TB: {TB:^5}| TT: {TT:^5}| TI: {TI:^5}| TF: {TF:>5}".format(proceso=self.nombre, TCC=self.tc, TE=self.tduracion, TVC=self.tvc, TB=self.tb, TT=self.tt, TI=self.ti, TF=self.tf)
        return datos 

# Ahora se crea la clase Microprocesador donde va a recibir la instruccion de ejecutar los procesos
# Aqui lo importante era ver si era necesario que el micro esperara en lo que el proceso que le toca se encuentra disponible = HUECO
# Actualiza el valor del TT que luego se le va a pasar a Proceso para que actualice los tiempos
# De igual forma se hizo un metodo __str__ que nos ayudaria a la hora de visualizar tanto el micro como los procesos que estan en ese micro
class Microprocesador:
    def __init__(self, id_micro, tc, tb, quantum):
        self.idm = id_micro
        self.tc = tc
        self.tb = tb
        self.quantum = quantum
        self.ocupado = False
        self.proceso = []
        self.tt = 0
    
    def gettt(self):
        return self.tt
    
    def ponerProceso(self,proceso):
        # Aqui es donde le decimos que haga un hueco si el proceso no esta disponible
        if self.tt < proceso.getinicio():
            tespera = proceso.getinicio() - self.tt
            self.ejecutarHueco(tespera)
        
        tcproceso = 0
        # Si el proceso no esta disponible, le asigna el valor de 0 a TC 
        if self.ocupado:
            tcproceso = self.tc
        
        #Aqui es donde se actualizan los valores de los tiempos iniciales y totales
        proceso.tiempos(self.tt, tcproceso, self.quantum, self.tb, self.tc)
        self.proceso.append(proceso)
        self.tt += proceso.gettt()
        self.ocupado = True

    def ejecutarHueco(self,t):
        # Aqui creamos un Proceso llamado Hueco que es basicamente el tiempo de espera
        # De esta manera igual se podra visualizar a la hora de imprimirlo 
        hueco = Proceso(0, "Hueco", t, 0)
        hueco.tiempos(self.tt, 0, t, 0, 0)
        self.proceso.append(hueco)
        self.tt += t
        self.ocupado = False
    
    # Aqui se van checando los procesos que sobraron para sacarlos y que de esta manera se encuentre ordenado
    def check(self):
        faltantes = 0
        for i in reversed(self.proceso):
            if i.getname() == "Hueco":
                faltantes += 1
            else:
                break
        for i in range(0, faltantes):
            self.proceso.pop()

    def __repr__(self):
        return "\nMicroprocesador: %s | %s" % (self.idm, self.proceso)

# Definimos nuestra clase Despachador que basicamente contiene la lista total de procesos a ejecutar
# Aqui definimos nuestros metodos para la seleccion de el mejor micro que en este caso lo hace dependiendo del id del micro y su tiempo total
# Asi nuestro despachador ya sabe a que micro mandar los procesos que faltan por ejecutarse
# Al final se hace la impresion de los valores que estan dentro del diccionario, en este caso nuestros micros  

class Despachador:
    def __init__(self, quantum, tb, tc, nmicros, procesos):
        self.quantum = quantum
        self.tb = tb
        self.tc = tc
        self.micros = []
        self.proceso = procesos

        for i in range(0, nmicros):
            self.micros.append({
                "num_micro": i+1,
                "tiempo_total": 0,
                "micro": Microprocesador(i+1, self.tc, self.tb, self.quantum)
            })

        self.ponerProceso()
        self.check()

    def ponerProceso(self):
        for i in self.proceso:
            # Se selecciona el mejor micro dependiendo del id y su tt
            # Hacemos que todos los micros esperen para que no ejecuten nada
            micro_ejecutado = self.bestMicro()
            if micro_ejecutado["micro"].gettt() < i.getinicio():
                for j in self.micros:
                    if j["micro"].gettt() < i.getinicio():
                        tespera = i.getinicio() - j["micro"].gettt()
                        j["micro"].ejecutarHueco(tespera)
                        j["tiempo_total"] = j["micro"].gettt()
                micro_ejecutado = self.bestMicro()
            micro_ejecutado["micro"].ponerProceso(i)
            micro_ejecutado["tiempo_total"] = micro_ejecutado["micro"].gettt()
        
    # Volvemos a sacar los procesos que sobran
    def check(self):
        for i in self.micros:
            i["micro"].check()

    # Buscamos en nuestro diccionario la llave de num_micro para que lo ordene primero por eso
    # Volvemos a ordenarlo, ahora usando como llave el tiempo_total     
    def bestMicro(self):
        mejormicro = sorted(self.micros, key=itemgetter('num_micro'))
        mejormicro = sorted(mejormicro, key=itemgetter('tiempo_total'))
        return mejormicro[0]

    # Hacemos una impresion especificamente de los valores que esten en 'micro' para no tener informacion de mas
    def printdespachador(self):
        i = 1
        for j in self.micros:
            if(j["num_micro"] == i):
                print()
                print (70 * "-")
                print(j['micro'])
            i += 1

if __name__ == '__main__':

    # Creamos nuestra lista de procesos siguiendo la definicion que hicimos en nuestra clase Procesos
    listaProcesos = []
    listaProcesos.append( Proceso(0, 'B', 300, 2))
    listaProcesos.append( Proceso(0, 'D', 100, 2))
    listaProcesos.append( Proceso(0, 'F', 500, 3))
    listaProcesos.append( Proceso(0, 'H', 700, 4))
    listaProcesos.append( Proceso(1500, 'J', 200, 2))
    listaProcesos.append( Proceso(1500, 'L', 3000, 5))
    listaProcesos.append( Proceso(1500, 'N', 50, 2))
    listaProcesos.append( Proceso(1500, 'O', 600, 3))
    listaProcesos.append( Proceso(3000, 'A', 400, 2))
    listaProcesos.append( Proceso(3000, 'C', 50, 2))
    listaProcesos.append( Proceso(3000, 'E', 1000, 5))
    listaProcesos.append( Proceso(3000, 'G', 10, 2))
    listaProcesos.append( Proceso(3000, 'I', 450, 3))
    listaProcesos.append( Proceso(4000, 'K', 100, 2))
    listaProcesos.append( Proceso(4000, 'M', 80, 2))
    listaProcesos.append( Proceso(4000, 'P', 800, 4))
    listaProcesos.append( Proceso(8000, 'Z', 500, 3))

    # Le pedimos al usuario los inputs
    print (30 * "-" , "INPUTS" , 30 * "-")
    micro = int(input("Introduce la cantidad de microprocesadores: "))
    q = int(input("Introduce el tamano del quantum: "))
    tiempo_c_c = int(input("Introduce el tiempo de cambio: "))
    tbloqueo = int(input("Introduce el tiempo de bloqueo: "))

    # Creamos nuestro despachador final, pasando como parametros los inputs y la lista de procesos
    # Finalmente imprimimos el producto final
    despachador_final = Despachador(q, tbloqueo, tiempo_c_c, micro, listaProcesos)
    despachador_final.printdespachador()

    print()