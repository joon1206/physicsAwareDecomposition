#include "costEulerImplicit.H"
#include "StandardChemistryModel.H"
#include "thermoPhysicsTypes.H"
#include "psiReactionThermo.H"
namespace Foam
{
typedef costEulerImplicit<StandardChemistryModel<psiReactionThermo,gasHThermoPhysics>> CostSolver;
defineTemplateTypeNameAndDebugWithName
(
    CostSolver,
    ("costEulerImplicit<standard<"+word(psiReactionThermo::typeName_())+","+gasHThermoPhysics::typeName()+">>").c_str(),
    0
);
BasicChemistryModel<psiReactionThermo>::addthermoConstructorToTable<CostSolver> addCostSolver;
}

#include "costOde.H"
namespace Foam {
typedef costOde<StandardChemistryModel<psiReactionThermo,gasHThermoPhysics>> CostOdeSolver;
defineTemplateTypeNameAndDebugWithName(CostOdeSolver,
("costOde<standard<"+word(psiReactionThermo::typeName_())+","+gasHThermoPhysics::typeName()+">>").c_str(),0);
BasicChemistryModel<psiReactionThermo>::addthermoConstructorToTable<CostOdeSolver> addCostOdeSolver;
}
