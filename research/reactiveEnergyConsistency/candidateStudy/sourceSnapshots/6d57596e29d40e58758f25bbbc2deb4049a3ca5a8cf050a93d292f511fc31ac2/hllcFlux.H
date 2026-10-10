/* GPL-3.0-or-later. Standard HLLC star flux; absolute thermochemical energy. */
{
    struct FaceFlux { scalar mass,energy,positive,negative;vector momentum; };
    auto hllc=[&](const scalar rL,const scalar rR,const vector& vL,const vector& vR,
        const scalar pL,const scalar pR,const scalar eiL,const scalar eiR,
        const scalar acL,const scalar acR,const vector& area)->FaceFlux
    {
        const scalar magArea=mag(area);const vector normal=area/magArea;
        const scalar uL=vL&normal,uR=vR&normal;
        const scalar SL=Foam::min(uL-acL,uR-acR),SR=Foam::max(uL+acL,uR+acR);
        const scalar EL=rL*(eiL+0.5*magSqr(vL)),ER=rR*(eiR+0.5*magSqr(vR));
        FaceFlux out;
        bool left=true;scalar massFlux=0,energyFlux=0;vector momentumFlux=vector::zero;
        if(SL>=0){massFlux=rL*uL;momentumFlux=rL*uL*vL+pL*normal;energyFlux=uL*(EL+pL);}
        else if(SR<=0){left=false;massFlux=rR*uR;momentumFlux=rR*uR*vR+pR*normal;energyFlux=uR*(ER+pR);}
        else
        {
            const scalar denom=rL*(SL-uL)-rR*(SR-uR);
            if(Foam::mag(denom)<VSMALL)FatalErrorInFunction<<"Degenerate HLLC wave estimate"<<exit(FatalError);
            const scalar SM=(pR-pL+rL*uL*(SL-uL)-rR*uR*(SR-uR))/denom;
            left=(SM>=0);
            const scalar r=left?rL:rR,pK=left?pL:pR,u=left?uL:uR,S=left?SL:SR,E=left?EL:ER;
            const vector v=left?vL:vR;
            const scalar starRho=r*(S-u)/(S-SM),starPressure=pK+r*(S-u)*(SM-u);
            if(starRho<=0 || starPressure<=0)FatalErrorInFunction<<"Inadmissible HLLC star state rho="<<starRho<<" p="<<starPressure<<exit(FatalError);
            const vector starU=v+(SM-u)*normal;
            const scalar starE=starRho*(E/r+(SM-u)*(SM+pK/(r*(S-u))));
            massFlux=r*u+S*(starRho-r);
            momentumFlux=r*u*v+pK*normal+S*(starRho*starU-r*v);
            energyFlux=u*(E+pK)+S*(starE-E);
        }
        out.mass=massFlux*magArea;out.momentum=momentumFlux*magArea;out.energy=energyFlux*magArea;
        out.positive=left?out.mass/rL:0;out.negative=left?0:out.mass/rR;
        return out;
    };
    forAll(phi,facei)
    {
        const FaceFlux out=hllc(rho_pos[facei],rho_neg[facei],U_pos[facei],U_neg[facei],
            p_pos[facei],p_neg[facei],e_pos[facei],e_neg[facei],
            cSf_pos[facei]/mesh.magSf()[facei],cSf_neg[facei]/mesh.magSf()[facei],mesh.Sf()[facei]);
        phi[facei]=out.mass;phiUp[facei]=out.momentum;phiEp[facei]=out.energy;
        aphiv_pos[facei]=out.positive;aphiv_neg[facei]=out.negative;
    }
    forAll(phi.boundaryField(),patchi)
    {
        forAll(phi.boundaryField()[patchi],facei)
        {
            const scalar areaMag=mesh.magSf().boundaryField()[patchi][facei];
            const FaceFlux out=hllc(rho_pos.boundaryField()[patchi][facei],rho_neg.boundaryField()[patchi][facei],
                U_pos.boundaryField()[patchi][facei],U_neg.boundaryField()[patchi][facei],
                p_pos.boundaryField()[patchi][facei],p_neg.boundaryField()[patchi][facei],
                e_pos.boundaryField()[patchi][facei],e_neg.boundaryField()[patchi][facei],
                cSf_pos.boundaryField()[patchi][facei]/areaMag,cSf_neg.boundaryField()[patchi][facei]/areaMag,
                mesh.Sf().boundaryField()[patchi][facei]);
            phi.boundaryFieldRef()[patchi][facei]=out.mass;phiUp.boundaryFieldRef()[patchi][facei]=out.momentum;phiEp.boundaryFieldRef()[patchi][facei]=out.energy;
            aphiv_pos.boundaryFieldRef()[patchi][facei]=out.positive;aphiv_neg.boundaryFieldRef()[patchi][facei]=out.negative;
        }
    }
}
