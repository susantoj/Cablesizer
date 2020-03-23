from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render
from sizer.models import CableData
from sizer.models import IecDerating
from sizer.models import IecAmpacity
from sizer.models import Acresistances
from sizer.models import Reactances
from sizer.models import EmailList
from datetime import datetime
from decimal import *
from math import *


# Main calculation view
# Templates: 'ampacity', 'voltdrop', 'sctemprise'
def main(request, template_name):
    c = {}
    c.update(csrf(request))
    
    # Initialise variables
    show_results = []
    load_amps = []
    show_calc = []
      
    # #######################
    # HOUSEKEEPING
    # #######################
    
    # On page load, get session cookies or set default values for first level
    if (request.method != 'POST'):
        if "volts" in request.session:
            volt_query = request.session["volts"]
        else:
            volt_query = 400
        
        if "load_kw" in request.session:
            load_query = request.session["load_kw"]
        else:        
            load_query = 30
        
        if "pf" in request.session:
            pf_query = request.session["pf"]
        else:  
            pf_query = 0.8
        
        if "eff" in request.session:
            eff_query = request.session["eff"]
        else:  
            eff_query = 0.9
        
        if "amps" in request.session:
            amps_query = request.session["amps"]
        else:
            amps_query = ''
        
        if "insulation" in request.session:
            insulation_query = request.session["insulation"]
            
        if "nocores" in request.session:
            nocores_query = request.session["nocores"]
            
        if "cond" in request.session:
            cond_query = request.session["cond"]
            
        if "phases" in request.session:
            phases_query = request.session["phases"]
        
        if template_name == "ampacity":
            if "ref_method" in request.session:
                refmethod_query = request.session["ref_method"]
            else:
                refmethod_query = "A"
            
            if "amb_temp" in request.session:
                ambtemp_query = request.session["amb_temp"]
            
            if "review_ampcalc" in request.session:
                show_calc = 1
        
        if template_name == "voltdrop":
            if "cablerun" in request.session:
                cablerun_query = request.session["cablerun"]
            else:
                cablerun_query = 100
            
            if "selectedsize" in request.session:
                selectedsize_query = request.session["selectedsize"]
                
            if "review_vdcalc" in request.session:
                show_calc = 1
        
        if template_name == "sctemprise":
            if "fault_level" in request.session:
                faultlevel_query = request.session["fault_level"]
            else:
                faultlevel_query = 10
                
            if "fault_time" in request.session:
                faulttime_query = request.session["fault_time"]
            else:
                faulttime_query = 0.01
                
            if "initial_temp" in request.session:
                initialtemp_query = request.session["initial_temp"]
            else:
                initialtemp_query = "75"
                
            if "final_temp" in request.session:
                finaltemp_query = request.session["final_temp"]
            else:
                finaltemp_query = "160"
            
            if "review_sccalc" in request.session:
                show_calc = 1
        
    # On button press, set session cookies
    if (request.method == 'POST'):

        # Setup common parameters and set cookies
        insulation_query = request.POST.get('insulation', '')
        request.session["insulation"] = insulation_query
        
        cond_query = request.POST.get('cond_mat', '')
        request.session["cond"] = cond_query
        
        nocores_query = request.POST.get('no_cores', '')
        request.session["nocores"] = nocores_query
        
        volt_query = request.POST.get('load_volt', '')
        request.session["volts"] = volt_query
        
        load_query = request.POST.get('load_kw', '')
        request.session["load_kw"] = load_query
        
        pf_query = request.POST.get('load_pf', '')
        request.session["pf"] = pf_query
        
        eff_query = request.POST.get('load_eff', '')
        request.session["eff"] = eff_query
        
        phases_query = request.POST.get('no_phases','')
        request.session["phases"] = phases_query
        
        # Check if load current is inputted directly
        amps_query = request.POST.get('load_current', '') 
        if amps_query:
            request.session["amps"] = amps_query
            
        # For the ampacity template
        if template_name == "ampacity":
            refmethod_query = request.POST.get('ref_method', '')
            request.session["ref_method"] = refmethod_query
            
            # Setup derating factors and set cookies
            ambtemp_query = request.POST.get('amb_temp', '')
            request.session["amb_temp"] = ambtemp_query
            
            nocables_query = request.POST.get('no_cables', '')
            if nocables_query:
                request.session["no_cables"] = nocables_query
                
            insttype_query = request.POST.get('inst_type', '')
            if insttype_query:
                request.session["inst_type"] = insttype_query
                
            nolayers_query = request.POST.get('no_layers', '')
            if nolayers_query:
                request.session["no_layers"] = nolayers_query
                
            thermalres_query = request.POST.get('therm_res', '')
            if thermalres_query:
                request.session["thermal_res"] = thermalres_query
                
            ugspacing_query = request.POST.get('ug_spacing', '')
            if ugspacing_query:
                request.session["ug_spacing"] = ugspacing_query
        
        if template_name == "voltdrop":
            selectedsize_query = request.POST.get('selected_size','')
            request.session["selectedsize"] = selectedsize_query
            
            cablerun_query = request.POST.get('cable_run','')
            request.session["cablerun"] = cablerun_query
        
        if template_name == "sctemprise":
            faultlevel_query = request.POST.get('fault_level','')
            request.session["fault_level"] = faultlevel_query

            faulttime_query = request.POST.get('fault_time','')
            request.session["fault_time"] = faulttime_query
                
            initialtemp_query = request.POST.get('initial_temp','')
            request.session["initial_temp"] = initialtemp_query

            finaltemp_query = request.POST.get('final_temp','') 
            request.session["final_temp"] = finaltemp_query
        
    # Second level cookie retrieval for ampacity template
    if (request.method != 'POST') or (request.POST.__contains__('refmethod_update')):
        if "amb_temp" in request.session:
            ambtemp_query = request.session["amb_temp"]
        else:
            ambtemp_query = 25
            
        if "no_cables" in request.session:
            nocables_query = request.session["no_cables"]
        
        if "inst_type" in request.session:
            insttype_query = request.session["inst_type"]
        else:
            insttype_query = []
        
        if "no_layers" in request.session:
            nolayers_query = request.session["no_layers"]
        
        if "thermal_res" in request.session:
            thermalres_query = request.session["thermal_res"] 
        
        if "ug_spacing" in request.session:
            ugspacing_query = request.session["ug_spacing"]

    # ##################################
    # CALCULATION MODULE
    # ##################################
    if (request.method == 'POST') or (show_calc == 1):
        
        # Calculate load current for three phase or single phase loads
        if (amps_query == ''):
            try:
                if phases_query == "3":
                    load_amps = round(Decimal(load_query) / Decimal(pf_query) / Decimal(volt_query) / Decimal(eff_query) / Decimal(sqrt(3)) * Decimal(1000),4)
                else:
                    load_amps = round(Decimal(load_query) / Decimal(pf_query) / Decimal(volt_query) / Decimal(eff_query) * Decimal(1000),4)
                request.session["load_amps"] = load_amps
                if "amps" in request.session:
                    del request.session["amps"]
            except:
                load_amps = []
        else:
            load_amps = amps_query
            request.session["load_amps"] = load_amps
        
        # ################################
        # AMPACITY TEMPLATE
        # ################################
        if template_name == "ampacity":          
                       
            if (request.POST.__contains__('calc_ampacity')) or (show_calc == 1):
                show_results = 1
                                            
                # Get derating factors
                try:
                    if (refmethod_query == "D"):
                        # Soil temperature derating
                        temp_derating = IecDerating.objects.get(type="Soil_Temp", arg1=ambtemp_query, arg2=insulation_query)
                        
                        # Thermal resistivity derating
                        thermalres_derating = IecDerating.objects.get(type="Thermal_Resistivity", arg1=thermalres_query, arg2=insttype_query)
                        request.session["thermalres_derating"] = thermalres_derating.derating
                        
                        # Underground spacing deratings
                        if (insttype_query == "Direct"):
                            # Direct buried
                            ugspacing_derating = IecDerating.objects.get(type="UG_Spacing_Direct", arg1=ugspacing_query, arg2=nocables_query)
                        else:
                            # Buried in conduit
                            ugspacing_derating = IecDerating.objects.get(type="UG_Spacing_Conduit", arg1=nocores_query, arg2=ugspacing_query, arg3=nocables_query)
                        request.session["ugspacing_derating"] = ugspacing_derating.derating
                            
                        total_derating = round(Decimal(temp_derating.derating) * Decimal(thermalres_derating.derating) * Decimal(ugspacing_derating.derating),4)
                    else:
                        temp_derating = IecDerating.objects.get(type="Ambient_Temp", arg1=ambtemp_query, arg2=insulation_query)
                    
                        if (refmethod_query == "A" or refmethod_query == "B"):
                            group_derating = IecDerating.objects.get(type="Grouping_Single", arg1="Bunched", arg2=nocables_query)
                            group_ref = "Table B.52.17"
                            
                        if (refmethod_query == "C"):
                            if (insttype_query == "Wall"):
                                group_derating = IecDerating.objects.get(type="Grouping_Single", arg1="Wall", arg2=nocables_query)
                            else:
                                group_derating = IecDerating.objects.get(type="Grouping_Single", arg1="Ceiling", arg2=nocables_query)
                            group_ref = "Table B.52.17"
                    
                        if (refmethod_query == "E"):
                            if (insttype_query == "Air"):
                                group_derating = IecDerating.objects.get(type="Grouping_Single", arg1="Bunched", arg2=nocables_query)
                                group_ref = "Table B.52.17"
                            else:
                                group_derating = IecDerating.objects.get(type="Grouping_Multi_MC", arg1=insttype_query, arg2 = nolayers_query,arg3=nocables_query)
                                group_ref = "Table B.52.20"
                        
                        if (refmethod_query == "F"):
                            if (insttype_query == "Air"):
                                group_derating = IecDerating.objects.get(type="Grouping_Single", arg1="Bunched", arg2=nocables_query)
                                group_ref = "Table B.52.17"
                            else:
                                group_derating = IecDerating.objects.get(type="Grouping_Multi_SC", arg1=insttype_query, arg2 = nolayers_query, arg3=nocables_query)
                                group_ref = "Table B.52.21"
                                
                        if (refmethod_query == "G"):
                            total_derating = round(Decimal(temp_derating.derating),4)
                        else:
                            total_derating = round(Decimal(temp_derating.derating) * Decimal(group_derating.derating),4)
                            request.session["group_derating"] = group_derating.derating
                            request.session["group_ref"] = group_ref
                except:
                    total_derating = []
                
                # Reform reference installation methods (they are shown in the form as A to G, but there are actually subidivisions A1, A2, B1, etc depending on whether they are single core or multi-core)
                if (refmethod_query == "A"):
                    if nocores_query == "Multi":
                        refmethod = "A2"
                    else:
                        refmethod = "A1"
                elif (refmethod_query == "B"):
                    if nocores_query == "Multi":
                        refmethod = "B2"
                    else:
                        refmethod = "B1"
                elif (refmethod_query == "D"):
                    if insttype_query == "Direct":
                        refmethod = "D2"
                    else:
                        refmethod = "D1"
                else:
                    refmethod = refmethod_query
                
                # Determine IEC reference for ampacity
                if (refmethod_query == "E" or refmethod_query == "F" or refmethod_query == "G"):
                    if (cond_query == "Copper"):
                        if (insulation_query == "PVC"):
                            ampacity_ref = "Table B.52.10"
                        else:
                            ampacity_ref = "Table B.52.12"
                    else:
                        if (insulation_query == "PVC"):
                            ampacity_ref = "Table B.52.11"
                        else:
                            ampacity_ref = "Table B.52.13"
                else:
                    if (insulation_query == "PVC"):
                        if (phases_query == "2"):
                            ampacity_ref = "Table B.52.2"
                        else:
                            ampacity_ref = "Table B.52.4"
                    else:
                        if (phases_query == "2"):
                            ampacity_ref = "Table B.52.3"
                        else:
                            ampacity_ref = "Table B.52.5"
                
                # Calculate minimum ampacity cable size
                try:
                    ampacity_search = Decimal(load_amps) / Decimal(total_derating)  
                    qset = IecAmpacity.objects.filter(insulation=insulation_query, material=cond_query, no_cond=phases_query, ref_method=refmethod, ampacity__gt=Decimal(ampacity_search)).order_by('size')
                    min_size = qset[0].size
                    min_base_amps = qset[0].ampacity
                    min_amps = round(Decimal(qset[0].ampacity) * Decimal(total_derating),4)
                                                            
                    request.session["temp_derating"] = temp_derating.derating
                    request.session["total_derating"] = total_derating
                    request.session["true_ref_method"] = refmethod                   
                    request.session["ampacity_ref"] = ampacity_ref
                    request.session["min_size"] = min_size
                    request.session["min_amps"] = min_amps
                    request.session["min_base_amps"] = min_base_amps
                    request.session["review_ampcalc"] = 1
                except:
                    min_size = []
    
        # ######################
        # VOLTAGE DROP TEMPLATE
        # ######################
        if template_name == "voltdrop":
            show_results = 1
            try:
                if (nocores_query == "Single"):
                    X_c = Reactances.objects.get(cores="Single", type="Flat Touching", size=selectedsize_query, insulation=insulation_query)
                    if (insulation_query == "PVC"):
                        R_c = Acresistances.objects.get(size=selectedsize_query, nocores="Single", conductor=cond_query, temperature="75")
                    else:
                        R_c = Acresistances.objects.get(size=selectedsize_query, nocores="Single", conductor=cond_query, temperature="90")
                else:
                    X_c = Reactances.objects.get(cores="Multi", type="Circular", size=selectedsize_query, insulation=insulation_query)
                    if (insulation_query == "PVC"):
                        R_c = Acresistances.objects.get(size=selectedsize_query, nocores="Multi", conductor=cond_query, condtype="Circular", temperature="75")
                    else:
                        R_c = Acresistances.objects.get(size=selectedsize_query, nocores="Multi", conductor=cond_query, condtype="Circular", temperature="90")
                
                acos_phi = Decimal(sin(Decimal(acos(Decimal(pf_query)))))
                
                if (phases_query == "3"):
                    # Three phase volt drop
                    volt_drop = round((Decimal(R_c.resistance) * Decimal(pf_query) + Decimal(acos_phi) * Decimal(X_c.reactance)) * Decimal(sqrt(3)) * Decimal(load_amps) * Decimal(cablerun_query) / Decimal(1000),4)
                else:
                    # Single phase volt drop
                    volt_drop = round((Decimal(R_c.resistance) * Decimal(pf_query) + Decimal(acos_phi) * Decimal(X_c.reactance)) * Decimal(2) * Decimal(load_amps) * Decimal(cablerun_query) / Decimal(1000),4)
                percent_drop = round(Decimal(volt_drop) / Decimal(volt_query) * Decimal(100),4)
                
                request.session["R_c"] = R_c.resistance
                request.session["X_c"] = X_c.reactance
                request.session["volt_drop"] = volt_drop
                request.session["percent_drop"] = percent_drop
                request.session["review_vdcalc"] = 1
            except:
                volt_drop = []
        
        # ########################
        # SHORT CIRCUIT TEMPLATE
        # ########################
        if template_name == "sctemprise":
            show_results = 1
            
            try:
                # Calculate the short circuit constant factor k
                if (cond_query == "Copper"):
                    k = round(Decimal(226) * Decimal(sqrt(Decimal(log(Decimal(1) + (Decimal(finaltemp_query) - Decimal(initialtemp_query)) / (Decimal(234.5) + Decimal(initialtemp_query)))))), 4)
                else:
                    k = round(Decimal(148) * Decimal(sqrt(Decimal(log(Decimal(1) + (Decimal(finaltemp_query) - Decimal(initialtemp_query)) / (Decimal(228) + Decimal(initialtemp_query)))))), 4)
                
                # Calculate the minimum cable size
                min_sc = round(Decimal(sqrt(Decimal(faultlevel_query) * Decimal(faultlevel_query) * Decimal(1000000) * Decimal(faulttime_query))) / Decimal(k), 4)
                request.session["min_sc"] = min_sc
                request.session["k_factor"] = k
                request.session["review_sccalc"] = 1
            except:
                min_sc = []
                
    # Create a test object of a cable (which we'll delete when the session is over)
    # test_cable = CableData(user = 'test', voltage = volt_query, loadpower = load_query, pf = pf_query, efficiency = eff_query, loadcurrent = load_amps)
    # test_cable.save()
    
    html_template = '%s.html' % template_name
    return render(request, html_template, locals())
    
# Report page
def report(request):
       
    if ("review_sccalc" in request.session) or ("review_ampcalc" in request.session) or ("review_vdcalc" in request.session):
        show_report = 1
        
        # Get common session variables
        cond_mat = request.session["cond"]
        no_phases = request.session["phases"]
        no_cores = request.session["nocores"]
        volts = request.session["volts"]
        pf = request.session["pf"]
        insulation = request.session["insulation"]
        load_amps = request.session["load_amps"]
        
        if ("load_kw" in request.session):
            load_kw = request.session["load_kw"]
            eff = request.session["eff"]
        if ("amps" in request.session):
            amps = request.session["amps"]   
            
        if ("review_ampcalc" in request.session):
            show_ampcalc = 1
            true_ref_method = request.session["true_ref_method"]
            ref_method = request.session["ref_method"]
            amb_temp = request.session["amb_temp"]
            
            if ("no_cables" in request.session):
                no_cables = request.session["no_cables"]
            if ("inst_type" in request.session):
                inst_query = request.session["inst_type"]
                if inst_query == "Wall":
                    inst_type = "Directly on a wall"
                if inst_query == "Ceiling":
                    inst_type = "Under a ceiling"
                if inst_query == "Direct":
                    inst_type = "Direct buried"
                if inst_query == "Conduit":
                    inst_type = "Buried in conduit"
                if inst_query == "Air":
                    inst_type = "Installed in air"
                if inst_query == "Ladder_T":
                    inst_type = "Cable ladder, cleats, etc (touching)"
                if inst_query == "Ladder_S":
                    inst_type = "Cable ladder, cleats, etc (spaced)"
                if inst_query == "Tray_PHT":
                    inst_type = "Horizontal perforated cable tray (touching)"
                if inst_query == "Tray_PHS":
                    inst_type = "Horizontal perforated cable tray (spaced)"
                if inst_query == "Tray_PVT":
                    inst_type = "Vertical perforated cable tray (touching)"
                if inst_query == "Tray_PVS":
                    inst_type = "Vertical perforated cable tray (spaced)"
                if inst_query == "Tray_UT":
                    inst_type = "Unperforated cable tray (touching)",
                if inst_query == "Tray_PVTT":
                    inst_type = "In trefoil on vertical perforated cable tray (touching)"
                if inst_query == "Tray_PVTL":
                    inst_type = "Laid flat on vertical perforated cable tray (touching)"
                if inst_query == "Tray_PHTT":
                    inst_type = "In trefoil on horizontal perforated cable tray (touching)"
                if inst_query == "Tray_PHTL":
                    inst_type = "Laid flat on horizontal perforated cable tray (touching)"
                if inst_query == "Ladder_TT":
                    inst_type = "In trefoil on cable ladder, cleats, etc (touching)"
                if inst_query == "Ladder_TL":
                    inst_type = "Laid flat on cable ladder, cleats, etc (touching)"
                
            if ("no_layers" in request.session):
                no_layers = request.session["no_layers"]
            if ("thermal_res" in request.session):
                thermal_res = request.session["thermal_res"] 
            if ("ug_spacing" in request.session):
                ug_spacing = request.session["ug_spacing"]
            
            temp_derating = request.session["temp_derating"]
            if ("thermalres_derating" in request.session):
                thermalres_derating = request.session["thermalres_derating"]
            if ("ugspacing_derating" in request.session):
                ugspacing_derating = request.session["ugspacing_derating"]
            if ("group_derating" in request.session):
                group_derating = request.session["group_derating"]
            if ("group_ref" in request.session):
                group_ref = request.session["group_ref"]
            
            total_derating = request.session["total_derating"]
            if ("ampacity_ref" in request.session):
                ampacity_ref = request.session["ampacity_ref"]
                min_size = request.session["min_size"]
                min_amps = request.session["min_amps"]
                min_base_amps = request.session["min_base_amps"]
            
        if ("review_vdcalc" in request.session):
            show_vdcalc = 1
            cable_run = request.session["cablerun"]
            selected_size = request.session["selectedsize"]
            R_c = request.session["R_c"]
            X_c = request.session["X_c"]
            volt_drop = request.session["volt_drop"]
            percent_drop = request.session["percent_drop"]
            
        if ("review_sccalc" in request.session):
            show_sccalc = 1
            
            fault_level = Decimal(request.session["fault_level"]) * Decimal(1000)
            fault_time = request.session["fault_time"]
            k_factor = request.session["k_factor"]
            initial_temp = request.session["initial_temp"]
            final_temp = request.session["final_temp"]
            min_sc = request.session["min_sc"]
        
    else:
        show_report = []
    
    return render(request, 'report.html', locals())