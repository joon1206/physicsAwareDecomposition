#include "cvOde.H"
#include "StandardChemistryModel.H"
#include "thermoPhysicsTypes.H"
#include "psiReactionThermo.H"
namespace Foam
{
typedef cvOde<StandardChemistryModel<psiReactionThermo,gasHThermoPhysics>> CvOdeSolver;
defineTemplateTypeNameAndDebugWithName
(
    CvOdeSolver,
    ("cvOde<standard<"+word(psiReactionThermo::typeName_())+","+gasHThermoPhysics::typeName()+">>").c_str(),
    0
);
BasicChemistryModel<psiReactionThermo>::addthermoConstructorToTable<CvOdeSolver> addCvOdeSolver;
}
