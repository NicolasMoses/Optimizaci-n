import sys
import cplex
import os

TOLERANCE =10e-6 

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])
        
class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        self.M = 200

    def load(self,filename):
        # Abrimos el archivo.
        f = open(filename)

        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)
        
        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))
        
        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))
        
        # Cerramos el archivo.
        f.close()


def get_instance_data():
    file_location = sys.argv[1].strip()
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance
    
def populate_by_row(my_problem, data):
    x_var = {}  # variable binaria que vale 1 si el trabajador “t” realizó la orden “o” en el turno “h” en el día “d”, y 0 en caso contrario. 
    w_var = {}  # variable binaria que vale 1 si la orden o_i fue realizada, y 0 en caso contrario.
    s_var = {}  # variable binaria que vale 1 si el trabajador “t” trabajó en el día “d”, y 0 en caso contrario. 
    y_var = {}  # variable binaria que vale 1 si el trabajador “t” se encuentra en el grupo de remuneración “n” y 0 en caso contrario.
    q_var = {}  # variable continua que representa la cantidad total de órdenes de trabajo realizadas por trabajador “t”.
    qy_var = {} # variable continua que tiene la cantidad de órdenes totales realizadas por el trabajador “t” en el grupo de remuneración “n”

    # Agrego variables binarias base que representan si el trabajador t, realizo la orden o, durante el turno h y dia d:
    names_x = []
    for t in range(data.cantidad_trabajadores):
        for o in range(data.cantidad_ordenes):
            for h in range(5):
                for d in range(6):
                    # Crear nombres únicos para cada variable
                    variable_name = f"X_{t}_{o}_{h}_{d}"
                    names_x.append(variable_name)
                    x_var[(t,o,h,d)] = variable_name

    # Añadir las variables binarias a CPLEX
    my_problem.variables.add(
        names=names_x,     # Nombres de las variables
        types=['B'] * len(names_x),  # Definir todas como binarias
        lb=[0.0] * len(names_x),     # Límite inferior (0)
        ub=[1.0] * len(names_x)      # Límite superior (1)
    )

    # Agrego variables binarias (W) que representan si la orden fue realizada o no:
    names_w = []
    for o in range(data.cantidad_ordenes):
        # Crear nombres únicos para cada variable
        variable_name = f"W_{o}"
        names_w.append(variable_name)
        w_var[o] = variable_name


    
    # Añadir las variables binarias a CPLEX
    beneficios = []
    for o in range(data.cantidad_ordenes):
        beneficios.append(data.ordenes[o].beneficio)
    my_problem.variables.add(
        names=names_w,               # Nombres de las variables
        obj = beneficios,        # Coeficientes utilizados en la función objetivo, son los valores del beneficio de cada orden
        types=['B'] * len(names_w),  # Definir todas como binarias
        lb=[0.0] * len(names_w),     # Límite inferior (0)
        ub=[1.0] * len(names_w)      # Límite superior (1)
    )

    # Agrego variables binarias (S) que representan si el trabajador t trabajo el dia d:
    names_s = []
    for t in range(data.cantidad_trabajadores):
        for d in range(6):
            # Crear nombres únicos para cada variable
            variable_name = f"S_{t}_{d}"
            names_s.append(variable_name)
            s_var[(t,d)] = variable_name

    # Añadir las variables binarias a CPLEX
    my_problem.variables.add(
        names=names_s,     # Nombres de las variables
        types=['B'] * len(names_s),  # Definir todas como binarias
        lb=[0.0] * len(names_s),     # Límite inferior (0)
        ub=[1.0] * len(names_s)      # Límite superior (1)
    )
    
    # Agrego variables binarias (Y) que representan la categoria de numero de dias trabajados en la que se encuentra el trabajador t:
    names_y = []
    for t in range(data.cantidad_trabajadores):
        for n in range(1,5):
            # Crear nombres únicos para cada variable
            variable_name = f"Y_{t}_{n}"
            names_y.append(variable_name)
            y_var[(t,n)] = variable_name

    # Añadir las variables binarias a CPLEX
    my_problem.variables.add(
        names=names_y,     # Nombres de las variables
        types=['B'] * len(names_y),  # Definir todas como binarias
        lb=[0.0] * len(names_y),     # Límite inferior (0)
        ub=[1.0] * len(names_y)      # Límite superior (1)
    )

    #Ahora defino una variable nueva que representa la cantidad de ordenes ejecutada por cada trabajador t:
    names_q = []
    for t in range(data.cantidad_trabajadores):
        variable_name = f"Q_{t}"  # Cantidad de órdenes ejecutadas por trabajador t
        names_q.append(variable_name)
        q_var[t] = variable_name

    my_problem.variables.add(
        names=names_q,
        types=['C'] * len(names_q),  # Definir como continua
        lb=[0.0] * len(names_q),      # Límite inferior (0)
        ub=[data.cantidad_ordenes] * len(names_q)  # Límite superior (número máximo de órdenes)
    )

    # Por ultimo, defino una variable mas que sea la multiplicación de Q_t y Y_t_n:
    names_qy = []
    for t in range(data.cantidad_trabajadores):
        for n in range(1,5):
            variable_name = f"QY_{t}_{n}"
            names_qy.append(variable_name)
            qy_var[(t,n)] = variable_name

    my_problem.variables.add(
        names=names_qy,
        types=['C'] * len(names_qy),  
        lb=[0.0] * len(names_qy),      # Límite inferior (0)
        ub=[data.cantidad_ordenes] * len(names_qy),  # Límite superior (número máximo de órdenes)
        obj=[-1000,-1200,-1400,-1500] * data.cantidad_trabajadores
    )
    
    # Seteamos direccion del problema
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)
    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion.
    add_constraint_matrix(my_problem, data, x_var, y_var, s_var, w_var, q_var, qy_var)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')


def add_constraint_matrix(my_problem, data, x_var, y_var, s_var, w_var, q_var, qy_var):

## Restricciones de factibilidad
    # 1) Cada trabajador (t) solo puede estar haciendo una órden (o) por turno (h) por día (d):
    for t in range(data.cantidad_trabajadores):
        for h in range(5):
            for d in range(6):
                indices = []
                values = []
                for o in range(data.cantidad_ordenes):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0)
                my_problem.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=indices, val=values)],
                    senses=["L"],
                    rhs=[1.0]
                )

    # 2) Cuando una órden (o) es realizada (w_var = 1), esta se realiza con la asignación de la cantidad de trabajadores necesarios para resolver la órden T_o:
    for o in range(data.cantidad_ordenes):
        indices = []
        values = []
        for t in range(data.cantidad_trabajadores):
            for h in range(5):
                for d in range(6):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0)
        # Agregamos To * W_o a la restricción
        indices.append(w_var[o])
        values.append(-data.ordenes[o].trabajadores_necesarios)  # Coeficiente negativo para T_o * W_o porque los movemos al lado izquierdo de la restricción
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['E'], rhs=[0]) # Del lado derecho de la restricción va 0 porque pasamos al lado izquierdo lo otro restando

    # 3) Cada trabajador puede trabajar como máximo 4 turnos al día:
    for t in range(data.cantidad_trabajadores):
        for d in range(6):
            indices = []
            values = []
            for o in range(data.cantidad_ordenes):
                for h in range(5):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0)
            my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)],senses=["L"], rhs=[4])

    # 4) Cada trabajador puede trabajar como máximo 5 días por semana:
    for t in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for d in range(6):
                indices.append(s_var[(t,d)])
                values.append(1.0)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)],senses=["L"], rhs=[5])
    
    # Agrego esta restricción para conectar las X_tohd con los S_td
    for t in range(data.cantidad_trabajadores):
        for d in range(6):
            indices = []
            values = []
            for o in range(data.cantidad_ordenes):
                for h in range(5):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0) 
             # Agregamos To * W_o a la restricción
            indices.append(s_var[(t,d)])
            values.append(-4.0)  # Coeficiente negativo para T_o * W_o porque los movemos al lado izquierdo de la restricción       
            my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[0])

    # 5) En cada turno por día no puede haber más trabajadores asignados que el total de trabajadores disponibles en la empresa (NT):
    for h in range(5):
        for d in range(6):
            indices = []
            values = []            
            for t in range(data.cantidad_trabajadores):
                for o in range(data.cantidad_ordenes):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0)
            my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[0])

    # 6) Hay pares de órdenes de trabajo que no pueden ser satisfechas en turnos consecutivos de un trabajador (Ord_Confl_oi,oj):
    for oi, oj in data.ordenes_conflictivas:
        for t in range(data.cantidad_trabajadores):
            for h in range(4): #usamos range(4) para evitar que exceda el número de turnos. Si la orden conflictiva se hace en el 5to turno, entonces no hay problema.
                for d in range(6):
                    indices = [x_var[(t, oi, h, d)], x_var[(t, oj, h+1, d)]]
                    values=[1.0,1.0]
                    my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[1])

    # Repito lo anterior pero para que incluya las restricciones de los conflictos permutando el orden de oi,oj:
    for oi, oj in data.ordenes_conflictivas:
        for t in range(data.cantidad_trabajadores):
            for h in range(4): #usamos range(4) para evitar que exceda el número de turnos. Si la orden conflictiva se hace en el 5to turno, entonces no hay problema.
                for d in range(6):
                    indices = [x_var[(t, oj, h, d)], x_var[(t, oi, h+1, d)]]
                    values=[1.0,1.0]
                    my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[1])
    
    # 7) Hay pares de órdenes de trabajo correlativas oi,oj tal que si se resuelve la orden oi, entonces debe resolverse oj ese mismo día en el turno consecutivo:
    for oi, oj in data.ordenes_correlativas:
        for h in range(4):
            for d in range (6):
                for t in range(data.cantidad_trabajadores):
                    indices = [x_var[(t, oi, h, d)], x_var[(t, oj, h+1, d)]]
                    values=[1/data.ordenes[oi].trabajadores_necesarios,-1/data.ordenes[oj].trabajadores_necesarios]
                    my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[0])

    # 8) La diferencia entre el trabajador con más órdenes asignadas en la semana y el trabajador con menos órdenes no puede ser mayor a 10:
    for ti in range(data.cantidad_trabajadores):
        for tj in range(ti + 1, data.cantidad_trabajadores):  # ti != tj, eliminamos el caso ti = tj
            indices_ti = []
            indices_tj = []
            values_ti = []
            values_tj = []
    
            # Sumamos todas las órdenes asignadas a cada ti y tj
            for o in range(data.cantidad_ordenes):
                for h in range(5):
                    for d in range(6):
                        indices_ti.append(x_var[(ti, o, h, d)])
                        indices_tj.append(x_var[(tj, o, h, d)])
                        values_ti.append(1.0)
                        values_tj.append(1.0) 
            
            # Restricción 1: ti - tj <= 10
            indices_1 = indices_ti + indices_tj
            values_1 = values_ti + [-v for v in values_tj]  # coeficientes son 1 para ti y -1 para tj
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices_1, val=values_1)],
                senses=['L'],
                rhs=[10]
            )
    
            # Restricción 2: tj - ti <= 10
            indices_2 = indices_ti + indices_tj
            values_2 = [-v for v in values_ti] + values_tj  # coeficientes son -1 para ti y 1 para tj
            my_problem.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices_2, val=values_2)],
                senses=['L'],
                rhs=[10]
            )

    # 9) Se crea una variable Q_t que mide la cantidad de órdenes realizadas por trabajador durante toda la semana:
    for t in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for o in range(data.cantidad_ordenes):
            for h in range(5):
                for d in range(6):
                    indices.append(x_var[(t, o, h, d)])
                    values.append(1.0)
        indices.append(q_var[t])
        values.append(-1.0)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['E'], rhs=[0]) 

    # 10) Se crea la variable Yn,t para identificar el grupo de remuneración n al que corresponde el trabajador t :
    # Se restringe la cantidad de variables de grupo de remuneración n por trabajador t para que solo 1 pueda estar prendida para el mismo t
    for t in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for n in range(1,5):
            indices.append(y_var[(t,n)])
            values.append(1.0)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['E'], rhs=[1])
    
    # Se generan la restricciones para la cantidad de ordenes de trabajo realizadas por trabajador t (Qt) segun una lógica de implicación y discretización
    # región de Qt menor o igual a 5:
    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(1.0)
        indices.append(y_var[(t,1)])
        values.append(data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M + 5])
    
    # región de Qt mayor o igual a 6 y menor o igual a 10
    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(-1.0)
        indices.append(y_var[(t,2)])
        values.append(-data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M - 6])    
    
    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(1.0)
        indices.append(y_var[(t,2)])
        values.append(data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M + 10])

    # región de Qt mayor o igual a 11 y menor o igual a 15
    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(-1.0)
        indices.append(y_var[(t,3)])
        values.append(-data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M - 11])      

    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(1.0)
        indices.append(y_var[(t,3)])
        values.append(data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M + 15])

    # región mayor a 15
    indices = []
    values = []
    for t in range(data.cantidad_trabajadores):
        indices.append(q_var[t])
        values.append(-1.0)
        indices.append(y_var[(t,4)])
        values.append(-data.M)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['L'], rhs=[data.M - 16])     

    # 11) Se arma la variable QYn,t como la multiplicación de Qt y Yn,t para que sea la variable a introducir en la función objetivo.
    for t in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for n in range(1,5):
            indices.append(qy_var[(t,n)])
            values.append(1.0)
            indices.append(y_var[(t,n)])
            values.append(1.0)
        indices.append(q_var[t])
        values.append(-1.0)
        my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)], senses=['E'], rhs=[0])

# Restricciones Deseables

    # 12) Hay pares de trabajadores ti,tj que tienen conflictos que prefieren no ser asignados a una misma orden de trabajo:
    #for ti, tj in data.conflictos_trabajadores:
        #for o in range(data.cantidad_ordenes):
            #indices = []
            #values = []            
            #for h in range(5):
                #for d in range(6):
                    #indices.append(x_var[(ti, o, h, d)])
                    #values.append(1.0) 
                    #indices.append(x_var[(tj, o, h, d)])
                    #values.append(1.0)
        #my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)],senses=['L'],rhs=[1])

    # 13) Hay pares de órdenes oi,oj que son repetitivas por lo que sería bueno que un mismo trabajador no sea asignado a ambas:
    #for oi, oj in data.ordenes_repetitivas:
        #for t in range(data.cantidad_trabajadores):
            #indices = []
            #values = []
            #for h in range(5):
                #for d in range(6):
                    #indices.append(x_var[(t, oi, h, d)])
                    #values.append(1.0) 
                    #indices.append(x_var[(t, oj, h, d)])
                    #values.append(1.0)
            #my_problem.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indices, val=values)],senses=['L'],rhs=[1])

def solve_lp(my_problem, data):
    
    # Resolvemos el ILP.
    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ',objective_value)
    print('Status solucion: ',status_string,'(' + str(status) + ')')

    # Imprimimos las variables usadas.
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.
        if x_variables[i] > TOLERANCE:
            print('x_' + str(data.items[i].index) + ':' , x_variables[i])

def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)


if __name__ == '__main__':
    main()
