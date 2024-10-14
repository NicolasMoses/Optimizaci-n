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
    

def add_constraint_matrix(my_problem, data):
    
    # Restriccion generica
    indices = ...
    values = ...
    row = [indices,values]
    my_problem.linear_constraints.add(lin_expr=[row], senses=[...], rhs=[...])
    

def populate_by_row(my_problem, data):

    x_var = {}
    w_var = {}
    s_var = {}
    y_var = {}
    q_var = {}
    qv_var = {}


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


    # Agrego variables binarias que representan si la orden fue realizada o no:
    names_w = []
    for o in range(data.cantidad_ordenes):
        # Crear nombres únicos para cada variable
        variable_name = f"W_{o}"
        names_w.append(variable_name)
        w_var[o] = variable_name


    
    # Añadir las variables binarias a CPLEX
    beneficios = [orden.beneficio for orden in instance.ordenes]
    my_problem.variables.add(
        names=names_w,               # Nombres de las variables
        obj = beneficios        # Coeficientes utilizados en la función objetivo, son los valores del beneficio de cada orden
        types=['B'] * len(names_w),  # Definir todas como binarias
        lb=[0.0] * len(names_w),     # Límite inferior (0)
        ub=[1.0] * len(names_w)      # Límite superior (1)
    )


    # Agrego variables binarias que representan si el trabajador t trabajo el dia d:
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
    

    # Agrego variables binarias que representan la categoria de numero de dias trabajados en la que se encuentra el trabajador t:
    names_y = []
    for t in range(data.cantidad_trabajadores):
        for n in range(4):
            # Crear nombres únicos para cada variable
            variable_name = f"Y_{n}_{t}"
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
        for n in range(4):
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
