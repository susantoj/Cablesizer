from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from nec.models import NecAmpacity
from nec.models import NecImpedance
from decimal import *
from math import *


# Main calculation view
# Templates: 'ampacity', 'voltdrop'
def main(request, template_name):
    c = {}
    c.update(csrf(request))

    # Initialise variables
    show_results = []
    load_amps = []
    show_calc = []
    incompat_type = []
    temp_warning = []
    total_derating = []
    full_load = []
    over_load = []

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

        if "loadtype" in request.session:
            loadtype_query = request.session["loadtype"]
        else:
            loadtype_query = "General"

        if "load_cont" in request.session:
            cont_query = request.session["load_cont"]
        else:
            if "load_noncont" not in request.session:
                cont_query = 10

        if "load_noncont" in request.session:
            noncont_query = request.session["load_noncont"]
        else:
            noncont_query = 0

        if "prot_device" in request.session:
            prot_query = request.session["prot_device"]
        else:
            prot_query = 16

        if "amps" in request.session:
            amps_query = request.session["amps"]
        else:
            amps_query = ''

        if "cabletype" in request.session:
            cabletype_query = request.session["cabletype"]
        else:
            cabletype_query = "TW"

        if "nocores" in request.session:
            nocores_query = request.session["nocores"]

        if "cond" in request.session:
            cond_query = request.session["cond"]
        else:
            cond_query = "Copper"

        if "phases" in request.session:
            phases_query = request.session["phases"]

        if template_name == "ampacity":
            if "inst_method" in request.session:
                instmethod_query = request.session["inst_method"]
            else:
                instmethod_query = "Raceways"

            if "review_nec_ampcalc" in request.session:
                show_calc = 1

        if template_name == "voltdrop":
            if "cablerun" in request.session:
                cablerun_query = request.session["cablerun"]
            else:
                cablerun_query = 100

            if "selectedsize" in request.session:
                selectedsize_query = request.session["selectedsize"]

            if "review_nec_vdcalc" in request.session:
                show_calc = 1

    # On button press, set session cookies
    if (request.method == 'POST'):

        # Setup common parameters and set cookies
        cabletype_query = request.POST.get('cable_type', '')
        request.session["cabletype"] = cabletype_query

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

        loadtype_query = request.POST.get('load_type','')
        request.session["loadtype"] = loadtype_query

        cont_query = request.POST.get('load_cont', '')
        if cont_query:
            request.session["load_cont"] = cont_query
        else:
            del request.session["load_cont"]

        noncont_query = request.POST.get('load_non_cont', '')
        if noncont_query:
            request.session["load_noncont"] = noncont_query

        prot_query = request.POST.get('prot_device','')
        request.session["prot_device"] = prot_query

        # Check if load current is inputted directly
        amps_query = request.POST.get('load_current', '')
        if amps_query:
            request.session["amps"] = amps_query

        # For the ampacity template
        if template_name == "ampacity":
            instmethod_query = request.POST.get('inst_method', '')
            request.session["inst_method"] = instmethod_query

            condtemp_query = request.POST.get('cond_temp', '')
            request.session["cond_temp"] = condtemp_query

            # Setup derating factors and set cookies
            ambtemp_query = request.POST.get('amb_temp', '')
            request.session["amb_temp"] = ambtemp_query

            # Check incompatible cable types
            if cond_query == "Aluminium":
                if cabletype_query == "FEP/FEPB" or cabletype_query == "MI" or cabletype_query == "ZW" or cabletype_query == "PFA" or cabletype_query == "PFAH" or cabletype_query == "TFE":
                    incompat_type = 1

            nocables_query = request.POST.get('no_cables', '')
            if nocables_query:
                request.session["no_cables"] = nocables_query

            insttype_query = request.POST.get('inst_type', '')
            if insttype_query:
                request.session["inst_type"] = insttype_query

        if template_name == "voltdrop":
            selectedsize_query = request.POST.get('selected_size','')
            request.session["selectedsize"] = selectedsize_query

            cablerun_query = request.POST.get('cable_run','')
            request.session["cablerun"] = cablerun_query

    # Second level cookie retrieval for ampacity template
    if (request.method != 'POST') or (request.POST.__contains__('refmethod_update')):
        if "amb_temp" in request.session:
            ambtemp_query = request.session["amb_temp"]
        else:
            ambtemp_query = 25

        if "cond_temp" in request.session:
            condtemp_query = request.session["cond_temp"]

        if "no_cables" in request.session:
            nocables_query = request.session["no_cables"]

        if "inst_type" in request.session:
            insttype_query = request.session["inst_type"]
        else:
            insttype_query = []

    # ##################################
    # CALCULATION MODULE
    # ##################################
    if (request.method == 'POST') or (show_calc == 1):

        # Calculate load current for three phase or single phase loads
        if (loadtype_query == 'General'):
            # General load
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
        else:
            # Service, feeder or branch load
            if not cont_query:
                cont_query = 0
            if not noncont_query:
                noncont_query = 0;
            max_load = round(Decimal(Decimal(cont_query) * Decimal(1.25) + Decimal(noncont_query)), 2)
            total_load = round(Decimal(Decimal(cont_query) + Decimal(noncont_query)), 2)
            if (Decimal(prot_query) > max_load) or (Decimal(prot_query) == total_load):
                load_amps = prot_query
            else:
                load_amps = max_load
            if (Decimal(prot_query) == total_load):
                full_load = 1
            request.session["load_amps"] = load_amps
            request.session["total_load"] = total_load
            request.session["max_load"] = max_load
        
        # ################################
        # AMPACITY TEMPLATE
        # ################################
        if template_name == "ampacity":

            if (request.POST.__contains__('calc_ampacity')) or (show_calc == 1):
                show_results = 1

                # Calculate derating factors
                try:
                    # Grouping or tray derating
                    if (instmethod_query == "Tray"):
                        if (nocores_query == "Multi"):
                            if (insttype_query == "Covered"):
                                group_derating = 0.95
                            else:
                                group_derating = 1
                            group_ref = "Article 392.80(A)(1)(B)"
                        else:
                            # Placeholder for single core cables (we need to calculate this later)
                            group_derating = 1
                            group_ref = "Article 392.80(A)(2)(B)"
                    else:
                        group_derating = nocables_query
                        group_ref = "Table 310.15(B)(3)(a)"

                    # Ambient temperature
                    amb_temp_F = round(Decimal(Decimal(ambtemp_query) * Decimal(9) / Decimal(5) + Decimal(32)),1)
                    if (instmethod_query == "Raceways"):
                        # If in raceways, incorporate the temperature adder for exposure to sunlight (Table 310.15(B)(3)(c))
                        eff_temp = Decimal(ambtemp_query) + Decimal(insttype_query)
                        if (insttype_query == "0"):
                            temp_adder_F = 0
                        if (insttype_query == "33"):
                            temp_adder_F = 60
                        if (insttype_query == "22"):
                            temp_adder_F = 40
                        if (insttype_query == "17"):
                            temp_adder_F = 30
                        if (insttype_query == "14"):
                            temp_adder_F = 25
                        eff_temp_F = round(Decimal(amb_temp_F) + Decimal(temp_adder_F),1)
                    else:
                        eff_temp = Decimal(ambtemp_query)
                        eff_temp_F = Decimal(amb_temp_F)

                    # Note there are different base temperatures for different cable types (30C or 40C)
                    condtemp_C = round(Decimal((Decimal(condtemp_query) - Decimal(32)) * Decimal(5) / Decimal(9)),1)
                    try:
                        if (condtemp_query == "140" or condtemp_query == "167" or condtemp_query == "194"):
                            temp_derating = round(Decimal(sqrt((Decimal(condtemp_C) - Decimal(eff_temp)) / (Decimal(condtemp_C) - Decimal(30)) )),4)
                        else:
                            temp_derating = round(Decimal(sqrt((Decimal(condtemp_C) - Decimal(eff_temp)) / (Decimal(condtemp_C) - Decimal(40)) )),4)
                    except:
                        temp_warning = 1

                    total_derating = round(Decimal(group_derating) * Decimal(temp_derating),4)
                except:
                    total_derating = []

                # For feeder loads, check that protective device > load
                if (loadtype_query == 'Feeder'):
                    if (Decimal(prot_query) < total_load):
                        over_load = 1
                        total_derating = []

                # Calculate minimum ampacity cable size
                try:
                    ampacity_search = Decimal(load_amps) / Decimal(total_derating)
                    if (instmethod_query == "Air" or instmethod_query == "Tray" and nocores_query == "Single"):
                        qset = NecAmpacity.objects.filter(installation="Air", cond=cond_query, cond_temp=condtemp_query, ampacity__gt=Decimal
    (ampacity_search)).order_by('metric_size')
                    else:
                        qset = NecAmpacity.objects.filter(installation="Raceways", cond=cond_query, cond_temp=condtemp_query, ampacity__gt=Decimal(ampacity_search)).order_by('metric_size')

                    # Do some extra work for single core cables in tray (due to different derating factors)
                    if (instmethod_query == "Tray" and nocores_query == "Single"):
                        # If the min size is greater than 1 AWG, then try search again with new deratings (1/0 AWG to 500kcmil)
                        if (qset[0].metric_size > 43):
                            if (insttype_query == "Covered"):
                                group_derating = 0.6
                            else:
                                group_derating = 0.65
                            total_derating = round(Decimal(group_derating) * Decimal(temp_derating),4)
                            ampacity_search = Decimal(load_amps) / Decimal(total_derating)
                            qset = NecAmpacity.objects.filter(installation="Air", cond=cond_query, cond_temp=condtemp_query, ampacity__gt=Decimal
    (ampacity_search)).order_by('metric_size')

                            # If the min size is greater than 500kcmil, then try search again with new deratings (>500kcmil)
                            if (qset[0].metric_size > 255):
                                if (insttype_query == "Covered"):
                                    group_derating = 0.7
                                else:
                                    group_derating = 0.75
                                total_derating = round(Decimal(group_derating) * Decimal(temp_derating),4)
                                ampacity_search = Decimal(load_amps) / Decimal(total_derating)
                                qset = NecAmpacity.objects.filter(installation="Air", cond=cond_query, cond_temp=condtemp_query, ampacity__gt=Decimal
        (ampacity_search)).order_by('metric_size')

                    # Prepare data for webpage
                    if (qset[0].metric_size > 110):
                        use_kcmil = 1
                    else:
                        use_kcmil = []

                    min_size = qset[0].size
                    min_base_amps = qset[0].ampacity
                    min_amps = round(Decimal(qset[0].ampacity) * Decimal(total_derating),4)
                    ampacity_ref = qset[0].reference

                    request.session["min_size_metric"] = qset[0].metric_size
                    request.session["group_derating"] = group_derating
                    request.session["group_ref"] = group_ref
                    request.session["eff_temp"] = eff_temp
                    request.session["temp_derating"] = temp_derating
                    request.session["total_derating"] = total_derating               
                    request.session["ampacity_ref"] = ampacity_ref
                    request.session["min_size"] = min_size
                    request.session["min_base_amps"] = min_base_amps
                    request.session["min_amps"] = min_amps
                    request.session["review_nec_ampcalc"] = 1
                except:
                    min_size = []

        # ######################
        # VOLTAGE DROP TEMPLATE
        # ######################
        if template_name == "voltdrop":
            show_results = 1

            if (loadtype_query == 'Feeder'):
                load_amps = total_load

            try:
                Z_c = NecImpedance.objects.get(size=selectedsize_query, cond=cond_query)
                acos_phi = Decimal(sin(Decimal(acos(Decimal(pf_query)))))

                if (phases_query == "3"):
                    # Three phase volt drop
                    volt_drop = round((Decimal(Z_c.r) * Decimal(pf_query) + Decimal(acos_phi) * Decimal(Z_c.x)) * Decimal(sqrt(3)) * Decimal(load_amps) * Decimal(cablerun_query) / Decimal(1000),4)
                else:
                    # Single phase volt drop
                    volt_drop = round((Decimal(Z_c.r) * Decimal(pf_query) + Decimal(acos_phi) * Decimal(Z_c.x)) * Decimal(2) * Decimal(load_amps) * Decimal(cablerun_query) / Decimal(1000),4)
                percent_drop = round(Decimal(volt_drop) / Decimal(volt_query) * Decimal(100),4)

                metric_size = Z_c.metric_size
                request.session["selectedmetric"] = metric_size
                request.session["R_c"] = Z_c.r
                request.session["X_c"] = Z_c.x
                request.session["volt_drop"] = volt_drop
                request.session["percent_drop"] = percent_drop
                request.session["review_nec_vdcalc"] = 1
            except:
                volt_drop = []

    html_template = 'nec_%s.html' % template_name
    return render(request, html_template, locals())


# Report page
def report(request):

    if ("review_nec_ampcalc" in request.session) or ("review_nec_vdcalc" in request.session):
        show_report = 1

        # Get common session variables
        cond_mat = request.session["cond"]
        no_phases = request.session["phases"]
        no_cores = request.session["nocores"]
        volts = request.session["volts"]
        pf = request.session["pf"]
        cable_type = request.session["cabletype"]
        load_amps = request.session["load_amps"]
        load_type = request.session["loadtype"]
        prot_device = request.session["prot_device"]

        if ("load_kw" in request.session):
            load_kw = request.session["load_kw"]
            eff = request.session["eff"]
        if ("amps" in request.session):
            amps = request.session["amps"]

        if ("load_cont" in request.session):
            cont_load = request.session["load_cont"]

        if ("load_noncont" in request.session):
            noncont_load = request.session["load_noncont"]

        if ("max_load" in request.session):
            max_load = request.session["max_load"]

        if ("total_load" in request.session):
            total_load = request.session["total_load"]
            if (Decimal(prot_device) == Decimal(total_load)):
                full_load = 1

        if ("review_nec_ampcalc" in request.session):
            show_ampcalc = 1

            inst_select = request.session["inst_method"]
            if (inst_select == "Tray"):
                inst_method = "Cable tray / ladder"
            else:
                if (inst_select == "Earth"):
                    inst_method = "Earth (Direct buried)"
                else:
                    inst_method = inst_select

            if ("no_cables" in request.session):
                no_cables = request.session["no_cables"]
            if ("inst_type" in request.session):
                inst_query = request.session["inst_type"]

            cond_temp = request.session["cond_temp"]
            cond_temp_C = round(Decimal((Decimal(cond_temp) - Decimal(32)) * Decimal(5) / Decimal(9)),1)
            amb_temp = request.session["amb_temp"]
            amb_temp_F = round(Decimal(Decimal(amb_temp) * Decimal(9) / Decimal(5) + Decimal(32)),1)
            eff_temp = request.session["eff_temp"]

            if (inst_select == "Raceways"):
                if (inst_query == "0"):
                    temp_adder_F = 0
                if (inst_query == "33"):
                    temp_adder_F = 60
                if (inst_query == "22"):
                    temp_adder_F = 40
                if (inst_query == "17"):
                    temp_adder_F = 30
                if (inst_query == "14"):
                    temp_adder_F = 25
            else:
                temp_adder_F = 0

            eff_temp_F = round(Decimal(amb_temp_F) + Decimal(temp_adder_F),1)
            
            temp_derating = request.session["temp_derating"]
            if ("group_derating" in request.session):
                group_derating = request.session["group_derating"]
            if ("group_ref" in request.session):
                group_ref = request.session["group_ref"]
            
            total_derating = request.session["total_derating"]
            if ("ampacity_ref" in request.session):
                ampacity_ref = request.session["ampacity_ref"]
                min_size = request.session["min_size"]
                min_size_metric = request.session["min_size_metric"]
                min_amps = request.session["min_amps"]
                min_base_amps = request.session["min_base_amps"]
                
        if ("review_nec_vdcalc" in request.session):
            show_vdcalc = 1
            cable_run = request.session["cablerun"]
            selected_size = request.session["selectedsize"]
            selected_metric = request.session["selectedmetric"]
            R_c = request.session["R_c"]
            X_c = request.session["X_c"]
            volt_drop = request.session["volt_drop"]
            percent_drop = request.session["percent_drop"]
        
    else:
        show_report = []

    for key, value in request.session.items():
        if type(value) == Decimal:
            request.session[key] = float(request.session[key])

    return render(request, 'nec_report.html', locals())
