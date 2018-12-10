import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        This function will do both Constraint Propagation and check
        the consistency of the network 
    """
    
    def forwardChecking ( self ):
        for v in self.network.variables:
            if v.isAssigned():
                valueAssigned = v.getAssignment()
                n = self.network.getNeighborsOfVariable(v)
                for item in n:
                    if item.getDomain().contains(valueAssigned):
                        self.trail.push(item)
                        item.removeValueFromDomain(v.getAssignment())
                    if item.size() == 0:
                        return False
        return True

    """
        This function will do both Constraint Propagation and check
        the consistency of the network
    """
    
    def norvigCheck ( self ):
        if not self.forwardChecking():
            return False
        for c in self.network.constraints:
            traceList = [0 for i in range(self.gameboard.N)]
            for v in c.vars:
                if v.isAssigned():
                    traceList[v.getAssignment()-1] = -1
                else:
                    vList = v.getValues()
                    for x in vList:
                        if traceList[x-1] != -1: 
                            traceList[x-1] += 1
            if 0 in traceList:
                return False
            for i,j in enumerate(traceList):
                if j == 1:
                    for v in c.vars:
                        if v.domain.contains(i+1):
                            self.trail.push(v)
                            v.assignValue(i+1)
                            break
        return True

   
    def getTournCC ( self ):
        if not self.forwardChecking():
            return False
        for c in self.network.constraints:
            traceList = [0 for i in range(self.gameboard.N)]
            for v in c.vars:
                if v.isAssigned():
                    traceList[v.getAssignment()-1] = -1
                else:
                    vList = v.getValues()
                    for x in vList:
                        if traceList[x-1] != -1: 
                            traceList[x-1] += 1
            if 0 in traceList:
                return False
            for i,j in enumerate(traceList):
                if j == 1:
                    for v in c.vars:
                        if v.domain.contains(i+1):
                            self.trail.push(v)
                            v.assignValue(i+1)
                            break
        return True
        

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    
    def getMRV ( self ):
        min_value = 100
        MRV = None
        for value in self.network.variables:
            if value.domain.size() <  min_value and value.isAssigned() == False :
                min_value = value.domain.size()
                MRV = value
        return MRV

    
    def getDegree ( self ):
        result = None
        max_value = 0
        for value in self.network.variables:
            if value.isAssigned() == False:
                counter = 0
                for neighbour in self.network.getNeighborsOfVariable(value):
                    if neighbour.isAssigned() == False:
                        counter += 1
                if result == None:
                    result = value
                if  max_value < counter:
                    max_value = counter
                    result = value
        return result

    
    def MRVwithTieBreaker ( self ):
        result = None
        max_value = 0
        for value in self.network.variables:
            if  value.isAssigned() == False:
                counter = 0
                for neighbour in self.network.getNeighborsOfVariable(value):
                    if  neighbour.isAssigned() == False:
                        counter += 1
                if result == None:
                    result = value
                elif result.domain.size() > value.domain.size():
                    result = value
                elif result.domain.size() == value.domain.size():
                    if  max_value <= counter:
                        max_value = counter
                        result = value            
        return result

    
    def getTournVar ( self ):
        min_value = 100
        MRV = None
        for value in self.network.variables:
            if value.domain.size() <  min_value and value.isAssigned() == False :
                min_value = value.domain.size()
                MRV = value
        return MRV
        

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    
    def getValuesLCVOrder ( self, v ):
        n = 0
        neighbors = self.network.getNeighborsOfVariable(v)
        counter = [0] * v.size()
        for neighbor in neighbors:
            for value in neighbor.domain.values: # 9
                try:
                    counter[v.domain.values.index(value)] += 1  
                except:
                    pass
        z = [(i,j) for i,j in zip(counter, v.domain.values)]
        z.sort()
        return [j for i,j in z]

   
    def getTournVal ( self, v ):
        n = 0
        neighbors = self.network.getNeighborsOfVariable(v)
        counter = [0] * v.size()
        for neighbor in neighbors:
            for value in neighbor.domain.values: # 9
                try:
                    counter[v.domain.values.index(value)] += 1  
                except:
                    pass
        z = [(i,j) for i,j in zip(counter, v.domain.values)]
        z.sort()
        return [j for i,j in z]
        

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
