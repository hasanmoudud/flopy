"""
mf module.  Contains the ModflowGlobal, ModflowList, and Modflow classes.


"""

import os
import sys
import flopy
from flopy.mbase import BaseModel, Package
from flopy.utils import mfreadnam
from flopy.modflow.mfpar import ModflowPar


class ModflowGlobal(Package):
    """
    ModflowGlobal Package class

    """

    def __init__(self, model, extension='glo'):
        Package.__init__(self, model, extension, 'GLOBAL', 1)
        return

    def __repr__(self):
        return 'Global Package class'

    def write_file(self):
        # Not implemented for global class
        return


class ModflowList(Package):
    """
    ModflowList Package class

    """

    def __init__(self, model, extension='list', unitnumber=2):
        Package.__init__(self, model, extension, 'LIST', unitnumber)
        return

    def __repr__(self):
        return 'List Package class'

    def write_file(self):
        # Not implemented for list class
        return


class Modflow(BaseModel):
    """
    MODFLOW Model Class.

    Parameters
    ----------
    modelname : string, optional
        Name of model.  This string will be used to name the MODFLOW input
        that are created with write_model. (the default is 'modflowtest')
    namefile_ext : string, optional
        Extension for the namefile (the default is 'nam')
    version : string, optional
        Version of MODFLOW to use (the default is 'mf2005').
    exe_name : string, optional
        The name of the executable to use (the default is
        'mf2005').
    listunit : integer, optional
        Unit number for the list file (the default is 2).
    model_ws : string, optional
        model workspace.  Directory name to create model data sets.
        (default is the present working directory).
    external_path : string
        Location for external files (default is None).
    verbose : boolean, optional
        Print additional information to the screen (default is False).
    load : boolean, optional
         (default is True).
    silent : integer
        (default is 0)

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()

    """

    def __init__(self, modelname='modflowtest', namefile_ext='nam',
                 version='mf2005', exe_name='mf2005.exe',
                 structured=True,
                 listunit=2, model_ws='.', external_path=None,
                 verbose=False, load=True, silent=0):
        BaseModel.__init__(self, modelname, namefile_ext, exe_name, model_ws, structured=structured)
        version_types = ('mf2k', 'mf2005', 'mfnwt', 'mfusg')
        self.heading = '# Name file for ' + version + ', generated by Flopy.'
        self.version = version.lower()
        if self.version == 'mf2k':
            self.glo = ModflowGlobal(self)
        self.lst = ModflowList(self, unitnumber=listunit)
        # -- check if unstructured is specified for something
        # other than mfusg is specified
        if not self.structured:
            assert 'mfusg' in self.version, 'structured=False can only be specified for mfusg models'

        # external option stuff
        self.free_format = True
        self.array_format = 'modflow'
        self.external_fnames = []
        self.external_units = []
        self.external_binflag = []
        self.external = False
        self.verbose = verbose
        self.load = load
        # the starting external data unit number
        self.__next_ext_unit = 1000
        if external_path is not None:
            assert model_ws == '.', "ERROR: external cannot be used " + \
                                    "with model_ws"

            #external_path = os.path.join(model_ws, external_path)
            if os.path.exists(external_path):
                print("Note: external_path " + str(external_path) +
                      " already exists")
            #assert os.path.exists(external_path),'external_path does not exist'
            else:
                os.mkdir(external_path)
            self.external = True
        self.external_path = external_path
        self.verbose = verbose
        self.silent = silent
        self.mfpar = ModflowPar()

        # Create a dictionary to map package with package object.
        # This is used for loading models.
        self.mfnam_packages = {
            "zone": flopy.modflow.ModflowZon,
            "mult": flopy.modflow.ModflowMlt,
            "pval": flopy.modflow.ModflowPval,
            "bas6": flopy.modflow.ModflowBas,
            "dis": flopy.modflow.ModflowDis,
            "bcf6": flopy.modflow.ModflowBcf,
            "lpf": flopy.modflow.ModflowLpf,
            "hfb6": flopy.modflow.ModflowHfb,
            "chd": flopy.modflow.ModflowChd,
            "wel": flopy.modflow.ModflowWel,
            "drn": flopy.modflow.ModflowDrn,
            "rch": flopy.modflow.ModflowRch,
            "evt": flopy.modflow.ModflowEvt,
            "ghb": flopy.modflow.ModflowGhb,
            "gmg": flopy.modflow.ModflowGmg,
            "riv": flopy.modflow.ModflowRiv,
            "str": flopy.modflow.ModflowStr,
            "swi2": flopy.modflow.ModflowSwi2,
            "pcg": flopy.modflow.ModflowPcg,
            "pcgn": flopy.modflow.ModflowPcgn,
            "nwt": flopy.modflow.ModflowNwt,
            "pks": flopy.modflow.ModflowPks,
            "sfr": flopy.modflow.ModflowSfr2,
            "sip": flopy.modflow.ModflowSip,
            "sor": flopy.modflow.ModflowSor,
            "de4": flopy.modflow.ModflowDe4,
            "oc": flopy.modflow.ModflowOc,
            "uzf": flopy.modflow.ModflowUzf1,
            "upw": flopy.modflow.ModflowUpw
        }
        return

    def __repr__(self):
        nrow, ncol, nlay, nper = self.get_nrow_ncol_nlay_nper()
        return 'MODFLOW %d layer(s), %d row(s), %d column(s), %d stress period(s)' % (nlay, nrow, ncol, nper)

    def next_ext_unit(self):
        """
        Function to encapsulate next_ext_unit attribute

        """
        self.__next_ext_unit += 1
        return self.__next_ext_unit

    @property
    def nlay(self):
        if (self.dis):
            return self.dis.nlay
        else:
            return 0

    @property
    def nrow(self):
        if (self.dis):
            return self.dis.nrow
        else:
            return 0

    @property
    def ncol(self):
        if (self.dis):
            return self.dis.ncol
        else:
            return 0

    @property
    def nper(self):
        if (self.dis):
            return self.dis.nper
        else:
            return 0


    def get_nrow_ncol_nlay_nper(self):
        dis = self.get_package('DIS')
        if (dis):
            return dis.nrow, dis.ncol, dis.nlay, dis.nper
        else:
            return 0, 0, 0, 0

    # Property has no setter, so read-only
    nrow_ncol_nlay_nper = property(get_nrow_ncol_nlay_nper)

    def get_ifrefm(self):
        bas = self.get_package('BAS6')
        if (bas):
            return bas.ifrefm
        else:
            return False

    def set_name(self, value):
        # Overrides BaseModel's setter for name property
        BaseModel.set_name(self, value)

        if self.version == 'mf2k':
            for i in range(len(self.glo.extension)):
                self.glo.file_name[i] = self.name + '.' + self.glo.extension[i]

        for i in range(len(self.lst.extension)):
            self.lst.file_name[i] = self.name + '.' + self.lst.extension[i]

    # Property must be redeclared to override basemodels setter method
    name = property(BaseModel.get_name, set_name)

    def write_name_file(self):
        """
        Write the model files.
        """
        fn_path = os.path.join(self.model_ws, self.namefile)
        f_nam = open(fn_path, 'w')
        f_nam.write('%s\n' % (self.heading))
        if self.version == 'mf2k':
            f_nam.write('{:12s} {:3d} {}\n'.format(self.glo.name[0], self.glo.unit_number[0], self.glo.file_name[0]))
        f_nam.write('{:12s} {:3d} {}\n'.format(self.lst.name[0], self.lst.unit_number[0], self.lst.file_name[0]))
        f_nam.write('{}'.format(self.get_name_file_entries()))
        for u, f, b in zip(self.external_units, self.external_fnames, self.external_binflag):
            if u == 0:
                continue
            fr = os.path.relpath(f, self.model_ws)
            if b:
                f_nam.write('DATA(BINARY)  {0:3d}  '.format(u) + fr + ' REPLACE\n')
            else:
                f_nam.write('DATA          {0:3d}  '.format(u) + fr + '\n')
        f_nam.close()
        return

    def load_results(self, **kwargs):

        # remove model if passed as a kwarg
        if 'model' in kwargs:
            kwargs.pop('model')

        hext = 'hds'
        dext = 'ddn'
        cext = 'cbc'

        savehead = False
        saveddn = False
        savebud = False

        # check for oc
        try:
            oc = self.get_package('OC')
            print(oc)
            hext = oc.extension[1]
            dext = oc.extension[2]
            cext = oc.extension[3]
            for k, lst in oc.stress_period_data.items():
                for v in lst:
                    if v.lower() == 'save head':
                        savehead = True
                    if v.lower() == 'save drawdown':
                        saveddn = True
                    if v.lower() == 'save budget':
                        savebud = True
        except:
            pass

        hpth = os.path.join(self.model_ws, '{}.{}'.format(self.get_name(), hext))
        dpth = os.path.join(self.model_ws, '{}.{}'.format(self.get_name(), dext))
        cpth = os.path.join(self.model_ws, '{}.{}'.format(self.get_name(), cext))

        hdObj = None
        ddObj = None
        bdObj = None

        if savehead and os.path.exists(hpth):
            hdObj = flopy.utils.HeadFile(hpth, model=self, **kwargs)

        if saveddn and os.path.exists(dpth):
            ddObj = flopy.utils.HeadFile(dpth, model=self, **kwargs)

        if savebud and os.path.exists(cpth):
            bdObj = flopy.utils.CellBudgetFile(cpth, model=self, **kwargs)

        return hdObj, ddObj, bdObj


    @staticmethod
    def load(f, version='mf2k', exe_name='mf2005.exe', verbose=False,
             model_ws='.', load_only=None):
        """
        Load an existing model.

        Parameters
        ----------
        f : MODFLOW name file
            File to load.
        
        model_ws : model workspace path

        load_only : (optional) filetype(s) to load (e.g. ["bas6", "lpf"])

        Returns
        -------
        ml : Modflow object

        Examples
        --------

        >>> import flopy
        >>> ml = flopy.modflow.Modflow.load(f)

        """
        # test if name file is passed with extension (i.e., is a valid file)
        if os.path.isfile(os.path.join(model_ws, f)):
            modelname = f.rpartition('.')[0]
        else:
            modelname = f

        # if model_ws is None:
        #    model_ws = os.path.dirname(f)
        if verbose:
            sys.stdout.write('\nCreating new model with name: {}\n{}\n\n'.
                             format(modelname, 50 * '-'))
        ml = Modflow(modelname, version=version, exe_name=exe_name,
                     verbose=verbose, model_ws=model_ws)

        files_succesfully_loaded = []
        files_not_loaded = []

        # read name file
        try:
            namefile_path = os.path.join(ml.model_ws, ml.namefile)
            ext_unit_dict = mfreadnam.parsenamefile(namefile_path,
                                                    ml.mfnam_packages,
                                                    verbose=verbose)
        except Exception as e:
            #print("error loading name file entries from file")
            #print(str(e))
            #return None
            raise Exception("error loading name file entries from file:\n" + str(e))

        if ml.verbose:
            print('\n{}\nExternal unit dictionary:\n{}\n{}\n'.
                  format(50 * '-', ext_unit_dict, 50 * '-'))

        # load dis
        dis = None
        dis_key = None
        for key, item in ext_unit_dict.items():
            if item.filetype.lower() == "dis":
                dis = item
                dis_key = key
                break
        try:
            pck = dis.package.load(dis.filename, ml,
                                   ext_unit_dict=ext_unit_dict)
            files_succesfully_loaded.append(dis.filename)
            if ml.verbose:
                sys.stdout.write('   {:4s} package load...success\n'
                                 .format(pck.name[0]))
            ext_unit_dict.pop(dis_key)
        except Exception as e:
            s = 'Could not read discretization package: {}. Stopping...' \
                .format(os.path.basename(dis.filename))
            raise Exception(s + " " + str(e))

        if load_only is None:
            load_only = []
            for key, item in ext_unit_dict.items():
                load_only.append(item.filetype)
        else:
            if not isinstance(load_only, list):
                load_only = [load_only]
            not_found = []
            for i, filetype in enumerate(load_only):
                filetype = filetype.upper()
                if filetype != 'DIS':
                    load_only[i] = filetype
                    found = False
                    for key, item in ext_unit_dict.items():
                        if item.filetype == filetype:
                            found = True
                            break
                    if not found:
                        not_found.append(filetype)
            if len(not_found) > 0:
                raise Exception("the following load_only entries were not found "
                                "in the ext_unit_dict: " + ','.join(not_found))


        # zone, mult, pval
        ml.mfpar.set_pval(ml, ext_unit_dict)
        ml.mfpar.set_zone(ml, ext_unit_dict)
        ml.mfpar.set_mult(ml, ext_unit_dict)

        # try loading packages in ext_unit_dict
        for key, item in ext_unit_dict.items():
            if item.package is not None:
                if item.filetype in load_only:
                    try:
                        pck = item.package.load(item.filename, ml,
                                                ext_unit_dict=ext_unit_dict)
                        files_succesfully_loaded.append(item.filename)
                        if ml.verbose:
                            sys.stdout.write('   {:4s} package load...success\n'
                                             .format(pck.name[0]))
                    except BaseException as o:
                        if ml.verbose:
                            sys.stdout.write('   {:4s} package load...failed\n   {!s}\n'
                                             .format(item.filetype, o))
                        files_not_loaded.append(item.filename)
                else:
                    if ml.verbose:
                        sys.stdout.write('   {:4s} package load...skipped\n'
                                         .format(item.filetype))
                    files_not_loaded.append(item.filename)
            elif "data" not in item.filetype.lower():
                files_not_loaded.append(item.filename)
                if ml.verbose:
                    sys.stdout.write('   {:4s} package load...skipped\n'
                                     .format(item.filetype))
            elif "data" in item.filetype.lower():
                if ml.verbose:
                    sys.stdout.write('   {} file load...skipped\n      {}\n'
                                     .format(item.filetype,
                                             os.path.basename(item.filename)))
                if key not in ml.pop_key_list:
                    ml.external_fnames.append(item.filename)
                    ml.external_units.append(key)
                    ml.external_binflag.append("binary"
                                               in item.filetype.lower())

        # pop binary output keys and any external file units that are now
        # internal
        for key in ml.pop_key_list:
            try:
                ml.remove_external(unit=key)
                ext_unit_dict.pop(key)
            except:
                if ml.verbose:
                    sys.stdout.write('Warning: external file unit " +\
                        "{} does not exist in ext_unit_dict.\n'.format(key))

        # write message indicating packages that were successfully loaded
        if ml.verbose:
            print(1 * '\n')
            s = '   The following {0} packages were successfully loaded.' \
                .format(len(files_succesfully_loaded))
            print(s)
            for fname in files_succesfully_loaded:
                print('      ' + os.path.basename(fname))
            if len(files_not_loaded) > 0:
                s = '   The following {0} packages were not loaded.'.format(
                    len(files_not_loaded))
                print(s)
                for fname in files_not_loaded:
                    print('      ' + os.path.basename(fname))
                print('\n')

        # return model object
        return ml
