/* GPL-3.0-or-later. Primitive h inversion of conserved absolute internal energy. */
{
    auto hcRecovery=thermo.hc();
    forAll(rho,i)
    {
        const scalar target=rhoE[i]/rho[i]-0.5*magSqr(U[i]);
        auto properties=[&](const scalar temperature,scalar& ha,scalar& cv,scalar& ea)
        {
            ha=0;cv=0;scalar gasConstant=0;
            forAll(Y,s)
            {
                const scalar cps=thermo.composition().Cp(s,p[i],temperature);
                const scalar cvs=thermo.composition().Cv(s,p[i],temperature);
                ha+=Y[s][i]*thermo.composition().Ha(s,p[i],temperature);
                cv+=Y[s][i]*cvs;gasConstant+=Y[s][i]*(cps-cvs);
            }
            ea=ha-gasConstant*temperature;
        };
        scalar lo=200,hi=5000,temperature=Foam::min(hi,Foam::max(lo,thermo.T()[i]));
        scalar ha=0,cv=0,ea=0;properties(lo,ha,cv,ea);const scalar lowEnergy=ea;
        properties(hi,ha,cv,ea);const scalar highEnergy=ea;
        if(rho[i]<=0 || target<lowEnergy || target>highEnergy)
            FatalErrorInFunction<<"Unattainable conserved reference energy at cell "<<i<<exit(FatalError);
        bool converged=false;
        for(label iter=0;iter<80;++iter)
        {
            properties(temperature,ha,cv,ea);const scalar residual=ea-target;
            if(Foam::mag(residual)<1e-9+1e-13*Foam::mag(target)){converged=true;break;}
            if(cv<=0)FatalErrorInFunction<<"Nonpositive reference Cv"<<exit(FatalError);
            if(residual>0)hi=temperature;else lo=temperature;
            const scalar trial=temperature-residual/cv;
            temperature=(trial>lo && trial<hi)?trial:0.5*(lo+hi);
        }
        if(!converged)FatalErrorInFunction<<"Reference energy inversion failed"<<exit(FatalError);
        e[i]=ha-hcRecovery()[i]; // 'e' aliases the selected primitive sensible h.
        thermo.T()[i]=temperature; // Seed native h inversion with the verified Cv root.
    }
}
