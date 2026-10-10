#include <chrono>
#include "LoadBalancedChemistryModel.H"
#include "makeChemistryModel.H"
#include "psiReactionThermo.H"
#include "thermoPhysicsTypes.H"
#include "EulerImplicit.H"
#include "ode.H"
namespace Foam {
makeChemistryModelType(LoadBalancedChemistryModel,psiReactionThermo,gasHThermoPhysics);
typedef EulerImplicit<LoadBalancedChemistryModel<psiReactionThermo,gasHThermoPhysics>> StuttgartEuler;
defineTemplateTypeNameAndDebugWithName(StuttgartEuler,
("EulerImplicit<LoadBalancedChemistryModel<"+word(psiReactionThermo::typeName_())+","+gasHThermoPhysics::typeName()+">>").c_str(),0);
BasicChemistryModel<psiReactionThermo>::addthermoConstructorToTable<StuttgartEuler> addStuttgartEuler;
typedef ode<LoadBalancedChemistryModel<psiReactionThermo,gasHThermoPhysics>> StuttgartOde;
defineTemplateTypeNameAndDebugWithName(StuttgartOde,
("ode<LoadBalancedChemistryModel<"+word(psiReactionThermo::typeName_())+","+gasHThermoPhysics::typeName()+">>").c_str(),0);
BasicChemistryModel<psiReactionThermo>::addthermoConstructorToTable<StuttgartOde> addStuttgartOde;
}
