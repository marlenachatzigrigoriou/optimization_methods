from VRP_Model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None
       
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None
        self.diff = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9
        self.diff = 0

class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9


class CustomerInsertionAllPositions(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.cost = 10 ** 9


class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.searchTrajectory = []
        self.overallBestSol = None
        self.rcl_size = 5
        self.tabulist = []
        self.tabulist_size = 30
        self.minTabuTenure = 10
        self.maxTabuTenure = 50


    def solve(self):

        file1 = open("sol_8180070.txt","w") 
        random.seed(101)
        o = 0

        for i in range(20):
            self.SetRoutedFlagToFalseForAllCustomers()
            self.sol = Solution()

            for j in range(25):
                rt = Route(self.depot, self.capacity)
                self.sol.routes.append(rt)

            self.ApplyNearestNeighborMethod(i)
            cc = self.sol.cost
            self.LocalSearch(1)
            self.LocalSearch(2)

            if self.overallBestSol == None or self.overallBestSol.cost > self.sol.cost:
                self.overallBestSol = self.cloneSolution(self.sol)
                o = i
            print(i, 'Const: ', cc, ' LS:', self.sol.cost, 'BestOverall: ', self.overallBestSol.cost)
            #self.ReportSolution(self.sol)
            #SolDrawer.draw(i, self.sol, self.allNodes)
         
        #print("final")
        self.ReportSolution(self.overallBestSol)
        self.ReportFinalSolution(self.overallBestSol, file1)
        SolDrawer.draw(o, self.overallBestSol, self.allNodes)
        return self.overallBestSol

    
    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False
            self.customers[i].isTabuTillIterator= -1


#######################################################################################

    def TestSolution(self):
        for r in range (0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            
            for n in range (0 , len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rt.cost += self.distanceMatrix[A.ID][B.ID]
                rt.load += A.demand
            if abs(rt.cost - rt.cost) > 0.0001:
                print ('Route Cost problem')
            if rt.load != rt.load:
                print('Route Load problem')

            if (rt.cost > self.sol.cost):
                self.sol.cost = rt.cost


    def ReportSolution(self, sol):
        difnodes = []
        pl, max = 0, 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
                if rt.sequenceOfNodes[j].ID not in difnodes:
                    difnodes.append(rt.sequenceOfNodes[j].ID)
                    pl += 1
            if rt.cost > max : max = rt.cost
            print(rt.cost, " | Route load: ", rt.load)
        print("Max solution route cost:", max, " | Solution number of nodes:", pl)


    def ReportFinalSolution(self, sol, file1):
        difnodes = []
        file1.write('%s\n' % sol.cost)
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes)-1):
                file1.write('%s' % rt.sequenceOfNodes[j].ID) 
                if j != len(rt.sequenceOfNodes) - 2: file1.write(',')
                if rt.sequenceOfNodes[j].ID not in difnodes:
                    difnodes.append(rt.sequenceOfNodes[j].ID)
            file1.write('\n')

##########################################################################################


    def ApplyNearestNeighborMethod(self, itr):
        modelIsFeasible = True
        insertions = 0
        bicl = []
        bicl_size = 2

        while (insertions < len(self.customers)):

            for r in range(len(self.sol.routes)):
                rt: Route = self.sol.routes[r]
                bestInsertion = CustomerInsertion()
                self.IdentifyBestInsertion(bestInsertion, rt, itr)

                if (bestInsertion.customer is not None):

                    routecost_updated = rt.cost + bestInsertion.cost

                    if len(bicl) < bicl_size:
                        new_tup = (bestInsertion, routecost_updated)
                        bicl.append(new_tup)
                        bicl.sort(key=lambda x: x[1])

                    elif routecost_updated < bicl[-1][1]:
                        bicl.pop(len(bicl) - 1)
                        new_tup = (bestInsertion, routecost_updated)
                        bicl.append(new_tup)
                        bicl.sort(key=lambda x: x[1])

            if len(bicl) > 0:
                tup_index = random.randint(0, len(bicl) - 1)
                tpl = bicl[tup_index]

                if (tpl[0].customer is not None):
                    self.ApplyCustomerInsertion(tpl[0])
                    insertions += 1
                    bicl = []
                else:
                    if (len(tpl[0].route.sequenceOfNodes) == 2):
                        modelIsFeasible = False
                    break

        if (modelIsFeasible == False):
            print('FeasibilityIssue')
           


    def IdentifyBestInsertion(self, bestInsertion, rt, itr):
        rcl = []
        for i in range(0, len(self.customers)):
            candidateCust:Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    trialCost = self.distanceMatrix[lastNodePresentInTheRoute.ID][candidateCust.ID]
                    if len(rcl) < self.rcl_size:
                        new_tup = (trialCost, candidateCust, rt)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
                    elif trialCost < rcl[-1][0]:
                        rcl.pop(len(rcl) - 1)
                        new_tup = (trialCost, candidateCust, rt)
                        rcl.append(new_tup)
                        rcl.sort(key=lambda x: x[0])
        if len(rcl) > 0:
            tup_index = random.randint(0, len(rcl) - 1)
            tpl = rcl[tup_index]
            bestInsertion.cost = tpl[0]
            bestInsertion.customer = tpl[1]
            bestInsertion.route = tpl[2]



    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)

        rt.cost += insertion.cost
        if (rt.cost> self.sol.cost):
            self.sol.cost = rt.cost

        rt.load += insCustomer.demand
        insCustomer.isRouted = True


##################################################################################3

    def cloneRoute(self, rt:Route):
        cloned = Route(self.depot, self.capacity)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.cost = self.sol.cost
        return cloned

    def InitializeOperators(self, sm, top):
        sm.Initialize()
        top.Initialize()



    def LocalSearch(self, operator):
            
            self.bestSolution = self.cloneSolution(self.sol)
            terminationCondition = False
            localSearchIterator = 0
            sm = SwapMove()
            top = TwoOptMove()
        
            while terminationCondition is False:

                self.InitializeOperators(sm, top)
               
                # Swaps
                if operator == 1:
                    self.FindBestSwapMove(sm, localSearchIterator)
                    if sm.positionOfFirstRoute is not None:
                        if sm.moveCost < 0:
                            self.ApplySwapMove(sm, localSearchIterator)
                        else:
                            terminationCondition = True
                #TwoOpt
                elif operator == 2:
                    self.FindBestTwoOptMove(top, localSearchIterator)
                    if top.positionOfFirstRoute is not None:
                        if top.diff < 0 and top.moveCost < 0:
                            self.ApplyTwoOptMove(top, localSearchIterator)
                        else:
                            terminationCondition = True
                       
                if (self.sol.cost < self.bestSolution.cost):
                    self.bestSolution = self.cloneSolution(self.sol)

                localSearchIterator = localSearchIterator + 1

            self.sol = self.bestSolution
    

###############################################################################################3

    def MoveIsTabu(self, n: Node, iterator, moveCost):
        if iterator < n.isTabuTillIterator:
            return True
        return False

    def MoveIsTabuList(self, current_tupple):
        for tl in range(len(self.tabulist)):
            if current_tupple[0] == self.tabulist[tl][0] and current_tupple[1] == self.tabulist[tl][1] and current_tupple[2] == self.tabulist[tl][2] and current_tupple[3] == self.tabulist[tl][3]:
                return True
    

    def SetTabuIterator(self, n: Node, iterator):
        n.isTabuTillIterator = iterator + random.randint(self.minTabuTenure, self.maxTabuTenure)

    def SetTabuIteratorList(self, reversed_tupple):        
        if len(self.tabulist) < self.tabulist_size:
            self.tabulist.append(reversed_tupple)
        else:
            self.tabulist.pop(0)
            self.tabulist.append(reversed_tupple)


###########################################################################################################
           
    
    def FindBestSwapMove(self, sm, iterator):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range (firstRouteIndex, len(self.sol.routes)):
                rt2:Route = self.sol.routes[secondRouteIndex]

                for firstNodeIndex in range (1, len(rt1.sequenceOfNodes) -1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1

                    for secondNodeIndex in range (startOfSecondNodeIndex, len(rt2.sequenceOfNodes) -1):

                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]    
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]        
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]    

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]   
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]       
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]   

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1: 
                                costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                            else:
                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                            route1_updated = rt1.cost + moveCost
                            route2_updated = rt2.cost + moveCost

                        else:
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                            costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                            costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2
                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                            route1_updated = rt1.cost + costChangeFirstRoute
                            route2_updated = rt2.cost + costChangeSecondRoute
                        
                        if route1_updated < self.sol.cost and route2_updated < self.sol.cost:
                            if moveCost < sm.moveCost and abs(moveCost) > 0.0001:
                                self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

                          

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost
      

    def ApplySwapMove(self, sm, iterator):

        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]

        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if (rt1 == rt2):
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand

        self.sol.cost = self.CalculateTotalCost(self.sol)

      

    def CalculateTotalCost(self, sol): 
        max = 0
        for i in range (0, len(sol.routes)):
            rt = sol.routes[i]
            c = 0
            for j in range (0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                c += self.distanceMatrix[a.ID][b.ID]
            if c > max :
                max = c
        return max


#####################################################################################################

    def FindBestTwoOptMove(self, top, iterator): 
        
        current_cost = self.sol.cost

        for rtInd1 in range(0, len(self.sol.routes)):
            rt1:Route = self.sol.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.sol.routes)):
                rt2:Route = self.sol.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        moveCost = 10 ** 9
                        
                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue                                                                   
                                                                                                           
                            costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]  
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                            moveCost = costAdded - costRemoved                                            
                            tobe_updated = rt1.cost + moveCost

                        else:

                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and  nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue                   
                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue

                            if nodeInd1 < nodeInd2:
                                costAdded = self.distanceMatrix[A.ID][L.ID] + self.distanceMatrix[B.ID][K.ID]
                                costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                                moveCost = costAdded - costRemoved
                            else:
                                costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]
                                costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                                moveCost = costAdded - costRemoved
                            
                            copy1, copy2 = [], []
                            copy1 = rt1.sequenceOfNodes.copy()
                            copy2 = rt2.sequenceOfNodes.copy()
                            
                            cost1, cost2 =  self.ApplyCheck(copy1, copy2, nodeInd1, nodeInd2)
                            tobe_updated = max(cost1, cost2)


                        current_tupple = (rt1, rt2, nodeInd1, nodeInd2)
                        
                        flag = True
                        if self.MoveIsTabu(A, iterator, moveCost) or self.MoveIsTabu(K, iterator, moveCost) or self.MoveIsTabuList(current_tupple):
                            flag = False

                        if flag:
                            p = tobe_updated - current_cost 
                                                            
                            diff = 0.7*p + 0.3*moveCost
                            
                            if rt1 == rt2:
                                if rt1.cost == current_cost:
                                    if diff < 0 and diff < top.diff : 
                                        self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, top.moveCost, diff, top)
                            
                            elif rt1.cost == current_cost and tobe_updated == cost1 and diff < top.diff:
                                self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, top.moveCost, diff, top)

                            elif rt2.cost == current_cost and tobe_updated == cost2 and diff < top.diff: 
                                self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, top.moveCost, diff, top)

                            else: 
                                if moveCost < top.moveCost and abs(moveCost) > 0.0001:
                                    self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top.diff, top)
                                   


    def ApplyTwoOptMove(self, top, iterator): 

        rt1:Route = self.sol.routes[top.positionOfFirstRoute]
        rt2:Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1 : top.positionOfSecondNode + 1] = reversedSegment

            self.SetTabuIterator(rt1.sequenceOfNodes[top.positionOfFirstNode], iterator)
            self.SetTabuIterator(rt1.sequenceOfNodes[top.positionOfSecondNode], iterator)

            rt1.cost += top.moveCost

        else:
            if top.positionOfFirstNode < top.positionOfSecondNode:
                
                relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :]
                relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :] 

                del rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :] 
                del rt2.sequenceOfNodes[top.positionOfSecondNode + 1 :] 

                rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2) 
                rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1) 

                self.SetTabuIterator(rt1.sequenceOfNodes[top.positionOfFirstNode], iterator)
                self.SetTabuIterator(rt2.sequenceOfNodes[top.positionOfSecondNode], iterator)

                self.UpdateRouteCostAndLoad(rt1)
                self.UpdateRouteCostAndLoad(rt2)

            else:
                
                relocatedSegmentOfRt1 = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1:])
                relocatedSegmentOfRt2 = reversed(rt2.sequenceOfNodes[: top.positionOfSecondNode + 1]) 

                del rt1.sequenceOfNodes[top.positionOfFirstNode + 1 :] 
                del rt2.sequenceOfNodes[: top.positionOfSecondNode + 1] 
              
                rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2) 
                
                l, m = [], []
                for j in range(len(rt2.sequenceOfNodes)):
                    l.append(rt2.sequenceOfNodes[j])

                m.extend(relocatedSegmentOfRt1)
                rt2.sequenceOfNodes = m + l 
                
                self.UpdateRouteCostAndLoad(rt1)
                self.UpdateRouteCostAndLoad(rt2)

                self.SetTabuIterator(rt1.sequenceOfNodes[top.positionOfFirstNode], iterator)
                self.SetTabuIterator(rt1.sequenceOfNodes[top.positionOfFirstNode+1], iterator)

        reversed_tupple = (rt1, rt2, top.positionOfFirstNode, top.positionOfSecondNode)
        self.SetTabuIteratorList(reversed_tupple)

        self.sol.cost = self.CalculateTotalCost(self.sol)



    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

        if nodeInd1 < nodeInd2:
            
            rt1FirstSegmentLoad = 0
            for i in range(0, nodeInd1 + 1): 
                n = rt1.sequenceOfNodes[i]
                rt1FirstSegmentLoad += n.demand
            rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

            rt2FirstSegmentLoad = 0
            for i in range(0, nodeInd2 + 1):
                n = rt2.sequenceOfNodes[i]
                rt2FirstSegmentLoad += n.demand
            rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

            if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity): 
                return True
            if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity): 
                return True
        
        else: 

            rt1FirstSegmentLoad = 0
            for i in range(0, nodeInd1 + 1): 
                n = rt1.sequenceOfNodes[i]
                rt1FirstSegmentLoad += n.demand
            rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad 

            rt2FirstSegmentLoad = 0
            for i in range(nodeInd2 + 1, len(rt2.sequenceOfNodes)):
                n = rt2.sequenceOfNodes[i]
                rt2FirstSegmentLoad += n.demand
            rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad  
            
            if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity): 
                return True
            if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity): 
                return True

        return False



    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i+1]
            tc += self.distanceMatrix[A.ID][B.ID]
            tl += A.demand
        rt.load = tl
        rt.cost = tc

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, diff, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost
        top.diff = diff



    def ApplyCheck(self, copy1, copy2, nodeInd1, nodeInd2): 

        if nodeInd1 < nodeInd2:
            relocatedSegmentOfRt1 = copy1[nodeInd1 + 1 :] 
            relocatedSegmentOfRt2 = copy2[nodeInd2 + 1 :] 
            del copy1[nodeInd1 + 1 :] 
            del copy2[nodeInd2 + 1 :] 
            copy1.extend(relocatedSegmentOfRt2) 
            copy2.extend(relocatedSegmentOfRt1)
        
        else:

            relocatedSegmentOfRt1 = reversed(copy1[nodeInd1 + 1:])
            relocatedSegmentOfRt2 = reversed(copy2[: nodeInd2 + 1]) 
            del copy1[nodeInd1 + 1 :] 
            del copy2[: nodeInd2 + 1] 
            copy1.extend(relocatedSegmentOfRt2) 
            l, m = [], []
            for j in range(len(copy2)):
                l.append(copy2[j])
            m.extend(relocatedSegmentOfRt1)
            copy2 = m + l 

        tc = 0
        for i in range(0, len(copy1) - 1):
            A = copy1[i]
            B = copy1[i+1]
            tc += self.distanceMatrix[A.ID][B.ID]
        cost1 = tc
        tc = 0
        for i in range(0, len(copy2) - 1):
            A = copy2[i]
            B = copy2[i+1]
            tc += self.distanceMatrix[A.ID][B.ID]
        cost2 = tc

        return (cost1, cost2)
