from __future__ import print_function

import sys, os
import numpy as np
import h5py


def h5save_usr_qa_setup(material, log):
    '''
    A list of questions to be answered to initialize the CyGutz job.
    '''
    f = h5py.File('ginit.h5', 'a')
    if '/usrqa' in f:
        return
    usr_input = open("input.slog", 'w')
    print('\n' + " User inputs to initialize the G-RISB job.")
    # cut-off distance to determine the rotation group.
    dist_cut = -1.0
    if '-c' in sys.argv:
        dist_cut = float(sys.argv[sys.argv.index('-c') + 1])
        print(" The uniform dist_cut for extracting a centered" + \
                " cluster \n for symmetry evaluation = {}\n".format(dist_cut),
                file=log)
    f['/usrqa/dist_cut'] = dist_cut

    unit = 'rydberg'
    if '-u' in sys.argv:
        unit = sys.argv[sys.argv.index('-u') + 1]
    f['/usrqa/unit'] = unit

    # Spin symmetry breaking
    if '-spl' in sys.argv:
        spin_polarization = sys.argv[sys.argv.index('-spl') + 1]
    else:
        spin_polarization = get_usr_input(
                "\n Do you want to BREAK SPIN-SYMMETRY?", ['y', 'n'])
        print(spin_polarization, file=usr_input)
    f['/usrqa/spin_polarization'] = spin_polarization

    if spin_polarization == 'y':
        if '-bfield' in sys.argv:
            # unit eV/bohr magneton
            b_field = float(sys.argv[sys.argv.index('-bfield') + 1])
        else:
            b_field = raw_input(' Enter local B-field strength in unit of' +
                    ' eV/bohr magneton:\n ')
            b_field = float(b_field)
        f['/usrqa/bfield_ev_per_bohr_magneton'] = b_field

    # Orbital symmetry breaking
    if '-opl' in sys.argv:
        orbital_polarization = sys.argv[sys.argv.index('-opl') + 1]
    else:
        orbital_polarization = get_usr_input(
                "\n Do you want to COMPLETELY break orbital-symmetry?",
                ['y', 'n'])
        print(orbital_polarization, file=usr_input)
    f['/usrqa/full_orbital_polarization'] = orbital_polarization

    # Spin-orbit interaction.
    if '-soc' in sys.argv:
        spin_orbit_coup = sys.argv[sys.argv.index('-soc') + 1]
    else:
        spin_orbit_coup = get_usr_input(
                "\n Do you want to take into account the SPIN-ORBIT" +
                " interaction?", ['y', 'n'])
        print(spin_orbit_coup, file=usr_input)
    f['/usrqa/spin_orbit_coup'] = spin_orbit_coup

    if 'y' == spin_polarization == spin_orbit_coup:
        print('Warning: magnetism with spin-orbit coupling is in ' +
                'experimental stage.')

    # Crystal field
    if 'n' in orbital_polarization:
        if '-cf' in sys.argv:
            crystal_field = sys.argv[sys.argv.index('-cf') + 1]
        else:
            crystal_field = get_usr_input(
                    "\n Do you want to take into account the" +
                    " CRYSTAL FIELD effect?", ['y', 'n'])
            print(crystal_field, file=usr_input)
    else:
        crystal_field = 'y'
    f['/usrqa/crystal_field'] = crystal_field

    # Coulomb U
    if '-um' in sys.argv:
        lhub = sys.argv[sys.argv.index('-um') + 1]
    else:
        print("\n Please select the method to parametrize Coulomb U-matrix.\n"+
                " LHUB = 1: Slater-Condo parametrization.\n" +
                "        2: Kanamori parametrization (useful for models).\n" +
                "        0: Manual input.")
        lhub = get_usr_input(" Please select LHUB: ", ['1', '2', '0'])
        usr_input.write(lhub + '\n')
    lhub = int(lhub)
    f['/usrqa/u_matrix_type'] = lhub

    # Choose double counting functional
    if '-dc' in sys.argv:
         ldc = sys.argv[sys.argv.index('-dc') + 1]
    else:
        print("\n Please select method for U-interaction double counting.\n" +
                " LDC = 12: Recommended for LDA+G-RISB calculations.\n" +
                "           Standard double counting. \n" +
                "           (updating Vdc at each charge iteration, \n" +
                "           initial n0 to be provided.) \n" +
                "        2: Fix double counting potential \n" +
                "           (keep same Vdc/n0 at each charge iteration,\n" +
                "           n0 to be provided.) \n" +
                "        1: Standard double counting potential \n" +
                "           (n0 self-consistently determined.) \n" +
                "        0:  No double counting (useful for models). ")
        ldc = get_usr_input(" Please select LDC: ", ['12', '0', '1', '2'])
        usr_input.write(ldc + '\n')
    ldc = int(ldc)
    f['/usrqa/ldc'] = ldc

    # Equivalent atom indices
    if '-eqidx' in sys.argv:
        string_idx_equivalent_atoms = sys.argv[sys.argv.index('-eqidx') + 1]
        idx_equivalent_atoms = [
                int(s) for s in string_idx_equivalent_atoms.split()]
        if 'y' == spin_polarization != spin_orbit_coup:
            string_updn_list = sys.argv[sys.argv.index('-eqidx') + 2]
    else:
        idx_equivalent_atoms = material.get_EquivalentAtoms() \
                ['equivalent_atoms'].tolist()
        yn = get_usr_input("\n Symmetrically-equivalent atom indices: " \
                + ''.join("%2d " % (i) for i in idx_equivalent_atoms) +
                "\n (note: '0 0 0 1 1' means 1-3 and 4-5 are two" +
                " inequivalent atoms). \n Accept?", ['y', 'n'])
        print(yn, file=usr_input)

        if yn == 'n':
            while True:
                string_idx_equivalent_atoms = raw_input(
                    " Enter user-defined equivalent atom indices: ")
                yn1 = get_usr_input(
                        "\n User-defined equivalent atom indices: " +
                        string_idx_equivalent_atoms + ". Accept?", ['y', 'n'])
                if yn1 == 'y':
                    idx_equivalent_atoms = [
                            int(s) for s in string_idx_equivalent_atoms.split()]
                    print(string_idx_equivalent_atoms, file=usr_input)
                    print(yn1, file=usr_input)
                    break

        if 'y' == spin_polarization != spin_orbit_coup:
            string_updn_list = raw_input(
                    "\n Enter up(1) dn(-1) or 0 for spin-moment of the atoms"+
                    "\n separated by a blank space (e.g., '1 -1 ...'):\n ")

    if 'y' == spin_polarization != spin_orbit_coup:
        updn_full_list = [int(s) for s in string_updn_list.split()]

        # sanity check
        if len(updn_full_list) != len(idx_equivalent_atoms):
            raise ValueError('different number of elements in updn_full_list' +
                    ' and idx_equivalent_atoms!')
        for i, idx_equ in enumerate(idx_equivalent_atoms):
            if updn_full_list[i] != updn_full_list[idx_equ]:
                raise ValueError('different spin moment direction for ' +
                        'equivalent atom pair {}-{}!'.format(i, idx_equ))
        f['/usrqa/updn_full_list'] = updn_full_list

    f['/usrqa/idx_equivalent_atoms'] = idx_equivalent_atoms

    # asking user list of correlated atoms and relative information:
    if '-uniql' in sys.argv:
        ipos = sys.argv.index('-uniql')+1
        stmp = sys.argv[ipos]
        unique_corr_symbol_list = [s for s in stmp.split('-')]
        ipos += 1
        stmp = sys.argv[ipos]
        unique_df_list = [s for s in stmp.split('-')]
        if lhub > 0:
            ipos += 1
            stmp = sys.argv[ipos]
            unique_u_list = [float(s) for s in stmp.split('-')]
            ipos += 1
            stmp = sys.argv[ipos]
            unique_j_list = [float(s) for s in stmp.split('-')]
        if ldc > 1:
            ipos += 1
            stmp = sys.argv[ipos]
            unique_nf_list = [float(s) for s in stmp.split('-')]
    else:
        unique_df_list = []
        unique_corr_symbol_list = []
        unique_u_list = []
        unique_j_list = []
        unique_nf_list = []
        for i, s in enumerate(material.symbols):
            if s in material.symbols[:i]:
                continue

            print('\n ' + '-'*12 + "\n atom {} {}".format(i,s))
            correlated = get_usr_input("\n Is this atom correlated?",
                    ['y', 'n'])
            print(correlated, file=usr_input)
            if 'n' in correlated:
                continue
            unique_corr_symbol_list.append(s)

            df = get_usr_input_combo(
                    "\n Enter correlated shells?", ['s', 'p', 'd', 'f'])
            print(df, file=usr_input)
            unique_df_list.append(df)

            if lhub > 0:
                while True:
                    answer = raw_input(
                            '\n Please provide interaction parameters U,J ' +
                            '\n separated by a space (eV): ')
                    try:
                        answer = answer.split()
                        UJ = [np.float(answer[i]) for i in range(2)]
                        break
                    except:
                        pass
                print(answer, file=usr_input)
                unique_u_list.append(UJ[0])
                unique_j_list.append(UJ[1])

            if ldc > 1:
                while True:
                    answer = raw_input(
                            '\n Please provide initial guess of the number of' +
                            '\n localized {}-electrons: '.format(df))
                    try:
                        nf = float(answer)
                        break
                    except:
                        continue
                print(answer, file=usr_input)
                unique_nf_list.append(nf)

    f['/usrqa/unique_corr_symbol_list'] = unique_corr_symbol_list
    f['/usrqa/unique_df_list'] = unique_df_list
    if ldc > 1:
        f['/usrqa/unique_nf_list'] = unique_nf_list
    if lhub > 0:
        f['/usrqa/unique_u_list_ev'] = unique_u_list
        f['/usrqa/unique_j_list_ev'] = unique_j_list

    if '-newton' in sys.argv:
        lnewton = sys.argv.index('-newton')+1
    else:
        print("\n Please select the method to solve G-RISB equations.\n" +
                " LNEWTON = 0: Recommended.\n" +
                "              Modified Powell hybrid method (HYDRD1).\n" +
                "          -1: Broyden method. Faster for solutions with Z\n" +
                "              much larger than 0,\n" +
                "              e.g., magnetic calculations.")
        lnewton = get_usr_input(" Please select LNEWTON: ", ['-1', '0'])
        usr_input.write(lnewton + '\n')
    lnewton = int(lnewton)
    f['/usrqa/lnewton'] = lnewton

    if '-ed' in sys.argv:
        iembeddiag = sys.argv.index('-ed')+1
    else:
        print("\n Please select the method to solve embedding Hamiltonian.\n"+
                " LDIAG = -3: Valence truncation ED for S=0 (spin-singlet)\n"+
                "         -1: Valence truncation ED.\n" +
                "          0: HF (Hartree-Fock, experimental).\n" +
                "          1: CISD (Configuration interaction\n" +
                "             singles & doubles based on HF, experimental).\n"+
                "         10: HF (Mixing one-particle density-matrix)")
        iembeddiag = get_usr_input(" Please select LDIAG: ",
                ['-3', '-1', '0', '1', '10'])
        usr_input.write(iembeddiag + '\n')
    iembeddiag = int(iembeddiag)
    f['/usrqa/iembeddiag'] = iembeddiag
    usr_input.close()
    os.rename("input.slog", "init_ga.input")


def get_usr_input(message, accept_list):
    while True:
        answer = raw_input(
                message +
                " \n Pick one from [" +
                ', '.join(item for item in accept_list) + "]...")
        if answer not in accept_list:
            print(" Please pick an answer in the list!" + \
                    " Make your choice again.")
        else:
            break
    return answer


def get_usr_input_combo(message, accept_list):
    while True:
        answer = raw_input(
                message +
                " \n Pick one or combinations separated by blank space" +
                " \n from [" + ', '.join(item for item in accept_list) + "]...")
        if answer_valid(answer, accept_list):
            break
    return answer


def answer_valid(answer, accept_list):
    answer_list = answer.split()
    for ans in answer_list:
        if ans not in accept_list:
            return False
    return True

