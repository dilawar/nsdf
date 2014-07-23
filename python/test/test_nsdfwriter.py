# test_nsdfwriter.py --- 
# 
# Filename: test_nsdfwriter.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Created: Mon Jul 21 15:00:04 2014 (+0530)
# Version: 
# Last-Updated: 
#           By: 
#     Update #: 0
# URL: 
# Keywords: 
# Compatibility: 
# 
# 

# Commentary: 
# 
# 
# 
# 

# Change log:
# 
# 
# 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA.
# 
# 

# Code:
"""Tests for the NSDFWriter class."""

import sys
from collections import defaultdict
import numpy as np
from numpy import testing as nptest
import h5py as h5
from datetime import datetime
import unittest

sys.path.append('..')
import nsdf

uid__ = 0
def getuid():
    """Increment the global uid tracker and return the value.

    Returns:
        str representation of the uid integer.
    """
    global uid__
    uid__ += 1
    return str(uid__)


def create_ob_model_tree():
        """This creates a model tree of the structure:

        /model
        |
        |__Granule
        |       |
        |       |__granule_0
        |       |       |__gc_0
        |       |       |__...
        |       |       |__gc_19
         ... ... ...
        |       |
        |       |__granule_9
        |               |__gc_0
        |               |__...
        |               |__gc_19 
        |__Mitral
        |       |
        |       |__mitral_0
        |       |       |__mc_0
        |       |       |__...
        |       |       |__mc_14
         ... ... ...
        |       |
        |       |__mitral_9
        |               |__mc_0
        |               |__...
        |               |__mc_19
       

        """
        uid = 0
        model_tree = nsdf.ModelComponent('model', uid=getuid())
        granule = nsdf.ModelComponent('Granule', uid=getuid(),
                                            parent=model_tree)
        mitral = nsdf.ModelComponent('Mitral', uid=getuid(),
                                           parent=model_tree)
        granule_cells = [nsdf.ModelComponent('granule_{}'.format(ii),
                                                 uid=getuid(),
                                                 parent=granule)
                                                 for ii in range(10)]
        mitral_cells = [nsdf.ModelComponent('mitral_{}'.format(ii),
                                                   uid=getuid(),
                                                   parent=mitral)
                                                 for ii in range(10)]
        for cell in granule_cells:
            cell.add_children([nsdf.ModelComponent('gc_{}'.format(ii),
                                                uid=getuid())
                               for ii in range(20)])
        for cell in mitral_cells:
            cell.add_children([nsdf.ModelComponent('mc_{}'.format(ii),
                                                    uid=getuid())
                               for ii in range(15)])
        return {'model_tree': model_tree,
                'granule_population': granule,
                'mitral_population': mitral,
                'granule_cells': granule_cells,
                'mitral_cells': mitral_cells}
    
    
class TestNSDFWriter(unittest.TestCase):
    def setUp(self):
        self.mdict = create_ob_model_tree()
        
    def test_add_uniform_ds(self):
        """Add the soma (gc_0) all the granule cells in olfactory bulb model
        as data sources for uniformly sampled data.

        """
        tmp_file_path = 'test_add_uniform_data_sources.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        granule_somata = []
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    granule_somata.append(comp.uid)
        writer.add_uniform_ds('pop0',
                              granule_somata)
        try:
            uniform_ds = writer._fd['/map/uniform/pop0']
            ds = set([uid for uid in uniform_ds])
        except KeyError:
            self.fail('pop0 not created.')
        self.assertEqual(ds, set(granule_somata))
        os.remove(tmp_file_path)
            
    def test_adding_ds_creates_uniform_group(self):
        """Check that adding uniform data sources creates the '/uniform' group
        under '/map'

        """
        tmp_file_path = 'test_add_uniform_data_sources.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        granule_somata = []
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    granule_somata.append(comp.uid)
        writer.add_uniform_ds('pop0', granule_somata)
        try:
            uniform_group = writer._fd['map']['uniform']
        except KeyError:
            self.fail('/map/uniform group does not exist after'
                      ' adding uniform data sources')
        os.remove(tmp_file_path)
        
    def test_add_nonuniform_ds_homogeneous(self):
        """Add the soma (gc_0) all the granule cells in olfactory bulb model
        as data sources for nonuniformly sampled data.

        """
        self.fail('Refactor this')
        tmp_file_path = 'test_add_nonuniform_ds_h.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
        writer.add_nonuniform_ds('pop1', mitral_somata, True)
        try:
            nonuniform_ds = writer._fd['/map/nonuniform/pop1']
            ds = set([uid for uid in nonuniform_ds])
        except KeyError:
            self.fail('pop1 not created.')
        self.assertEqual(ds, set(mitral_somata))
        os.remove(tmp_file_path)
            
    def test_adding_ds_homogeneous_creates_nonuniform_group(self):
        """Check that adding nonuniform data sources creates the '/nonuniform'
        group under '/map'

        """
        tmp_file_path = 'test_add_nonuniform_ds_h1.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
        writer.add_nonuniform_ds('pop1',
                                mitral_somata, True)
        try:
            nonuniform_group = writer._fd['map']['nonuniform']
        except KeyError:
            self.fail('/map/nonuniform group does not exist after'
                      ' adding nonuniform data sources')
        os.remove(tmp_file_path)

    def test_add_nonuniform_ds_nonhomogeneous(self):
        """Add the soma (gc_0) all the granule cells in olfactory bulb model
        as data sources for nonuniformly sampled data.

        """
        tmp_file_path = 'test_add_nonuniform_ds_nh.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
        writer.add_nonuniform_ds('pop1', mitral_somata, False)
        try:
            nonuniform_ds = writer._fd['/map/nonuniform/pop1']
        except KeyError:
            self.fail('pop1 not created.')
        self.assertIsInstance(nonuniform_ds, h5.Group)
        os.remove(tmp_file_path)
            
    def test_adding_ds_nonhomogeneous_creates_nonuniform_group(self):
        """Check that adding nonuniform data sources creates the '/nonuniform'
        group under '/map'

        """
        tmp_file_path = 'test_add_nonuniform_ds_nh1.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
        writer.add_nonuniform_ds('pop1',
                                mitral_somata, False)
        try:
            nonuniform_group = writer._fd['map']['nonuniform']
        except KeyError:
            self.fail('/map/nonuniform group does not exist after'
                      ' adding nonuniform data sources')
        os.remove(tmp_file_path)
        
    def test_add_event_ds(self):
        """Add all the cells in olfactory bulb model as data sources for event
        data.

        """
        tmp_file_path = 'test_add_event_ds.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        writer.add_event_ds('cells')
        try:
            event_ds = writer._fd['/map/event/cells']
        except KeyError:
            self.fail('`cells` group not created.')
        self.assertIsInstance(event_ds, h5.Group)
        os.remove(tmp_file_path)                                
        
    def test_adding_ds_event_creates_event_group(self):
        """Check that adding nonuniform data sources creates the '/nonuniform'
        group under '/map'

        """
        tmp_file_path = 'test_add_event_ds.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        writer.add_event_ds('cells')
        try:
            nonuniform_group = writer._fd['map']['event']
        except KeyError:
            self.fail('/map/event group does not exist after'
                      ' adding event data sources')
        os.remove(tmp_file_path)

    def test_create_uniform_data(self):
        """Create uniform data for the first time."""
        tmp_file_path = 'test_create_uniform_data.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        granule_somata = []
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    granule_somata.append(comp.uid)
        ds = writer.add_uniform_ds('pop0',
                              granule_somata)
        datadict = {}
        dlen = 1000
        for uid in granule_somata:
            datadict[uid] = np.random.uniform(-65, -55, size=dlen)
        dt = 1e-4
        field = 'Vm'
        unit = 'mV'
        tstart = 0.0
        data = writer.add_uniform_data('Vm', ds, datadict,
                                          field=field,
                                          unit=unit,
                                          tstart=tstart,
                                          dt=dt, tunit='s')
        for row, source in zip(data, data.dims[0]['source']):
            nptest.assert_allclose(np.asarray(row), datadict[source])
        self.assertEqual(data.attrs['field'], field)
        self.assertEqual(data.attrs['unit'], unit)
        self.assertAlmostEqual(data.attrs['dt'], dt)
        self.assertAlmostEqual(data.attrs['tstart'], tstart)
        os.remove(tmp_file_path)

    def test_add_uniform_data(self):
        """Create uniform data for the first time."""
        tmp_file_path = 'test_add_uniform_data.h5'
        writer = nsdf.NSDFWriter(tmp_file_path, mode='w')
        granule_somata = []
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    granule_somata.append(comp.uid)
        ds = writer.add_uniform_ds('pop0',
                              granule_somata)
        datadict = {}
        dlen = 5
        for uid in granule_somata:
            datadict[uid] = np.random.uniform(-65, -55, size=dlen)
        dt = 1e-4
        field = 'Vm'
        unit = 'mV'
        tstart = 0.0
        data = writer.add_uniform_data('Vm', ds, datadict,
                                       field=field, unit=unit,
                                       tstart=tstart, dt=dt,
                                       tunit='s')
        del writer
        # start over for appending data
        writer = nsdf.NSDFWriter(tmp_file_path)
        granule_somata = []
        for cell in self.mdict['granule_cells']:
            for name, comp in cell.children.items():
                if name == 'gc_0':
                    granule_somata.append(comp.uid)
        ds = writer.mapping['uniform']['pop0']
        datadict = {}
        dlen = 5
        for uid in granule_somata:            
            datadict[uid] = np.random.uniform(-65, -55, size=dlen)
        dt = 1e-4
        field = 'Vm'
        unit = 'mV'
        tstart = 0.0
        data = writer.add_uniform_data('Vm', ds, datadict,
                                          field=field,
                                          unit=unit,
                                          tstart=tstart,
                                          dt=dt, tunit='s')
        for row, source in zip(data, data.dims[0]['source']):
            nptest.assert_allclose(np.asarray(row[-dlen:]), datadict[source])
        os.remove(tmp_file_path)

    def test_model_tree(self):
        """Check if model tree is created properly."""
        self.fail('Fix me.')

    def test_create_nonuniform_1d(self):
        """Check adding nonuniformly sampled data using 1D datasets for the
        first time"""
        tmp_file_path = 'test_create_nonuniform_1d.h5'
        writer = nsdf.NSDFWriter(tmp_file_path)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
        ds = writer.add_nonuniform_ds('pop1',
                              mitral_somata)
        datadict = {}
        dlen = 1000
        datalist = []
        src_name_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=dlen))
            datalist.append((uid, data, times))
            src_name_dict[uid] = str('vm_{}'.format(ii))
        field = 'Vm'
        unit = 'mV'
        tunit = 's'
        tstart = 0.0
        datadict = writer.add_nonuniform_1d('Vm', ds,src_name_dict,
                                        datalist, field=field,
                                        unit=unit, tunit=tunit)
        del writer
        os.remove(tmp_file_path)
        
        

    def test_add_nonuniform_vlen(self):
        self.fail('Fix me')

    def test_add_nonuniform_nan(self):
        self.fail('Fix me')

    def test_add_event_1d(self):
        self.fail('Fix me')

    def test_add_event_vlen(self):
        self.fail('Fix me')
        
    def test_add_event_nan(self):
        self.fail('Fix me')

class TestNSDFWriterNonuniform1D(unittest.TestCase):
    """Test case for writing nonuniformly sampled data in 1D arrays"""
    def setUp(self):
        self.mdict = create_ob_model_tree()
        self.filepath = 'test_nsdfwriter_nonuniform_1d.h5'
        self.writer = nsdf.NSDFWriter(self.filepath,
                                 dialect=nsdf.dialect.ONED)
        mitral_somata = []
        for cell in self.mdict['mitral_cells']:
            for name, comp in cell.children.items():
                if name == 'mc_0':
                    mitral_somata.append(comp.uid)
                    
        self.popname = 'pop1'
        ds = self.writer.add_nonuniform_ds(self.popname, mitral_somata)
        self.dlen = 1000
        self.datalist = []
        self.src_name_dict = {}
        self.src_data_dict = {}
        self.src_ts_dict = {}
        for ii, uid in enumerate(mitral_somata):
            data = np.random.uniform(-65, -55, size=self.dlen)
            times = np.cumsum(np.random.exponential(scale=0.01, size=self.dlen))
            self.datalist.append((uid, data, times))            
            self.src_name_dict[uid] = str('vm_{}'.format(ii))
            self.src_data_dict[uid] = data
            self.src_ts_dict[uid] = times
        self.field = 'Vm'
        self.unit = 'mV'
        self.tunit = 's'
        self.varname = 'Vm'
        dd = self.writer.add_nonuniform_1d(self.varname,
                                           ds,self.src_name_dict,
                                           self.datalist,
                                           field=self.field,
                                           unit=self.unit,
                                           tunit=self.tunit)
        del self.writer # ensure the file is closed

    def tearDown(self):        
        os.remove(self.filepath)
                                 
    def test_data(self):
        """Check the data is correctly written."""
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.varname)            
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                nptest.assert_allclose(np.asarray(self.src_data_dict[srcuid]),
                                       np.asarray(dataset))
                self.assertEqual(dataset.attrs['unit'], self.unit)
                self.assertEqual(dataset.attrs['field'], self.field)

    def test_ts(self):
        with h5.File(self.filepath, 'r') as fd:
            data_grp_name = '/data/{}/{}/{}'.format(nsdf.NONUNIFORM,
                                               self.popname,
                                               self.varname)
            data_grp = fd[data_grp_name]
            for dataset_name in data_grp:
                dataset = data_grp[dataset_name]
                srcuid = dataset.attrs['source']
                ts = dataset.dims[0]['time']
                nptest.assert_allclose(np.asarray(self.src_ts_dict[srcuid]),
                                       np.asarray(ts))
                self.assertEqual(ts.attrs['unit'], self.tunit)

        

        
def main():
    unittest.main()

import subprocess

if __name__ == '__main__':
    main()


# 
# test_nsdfwriter.py ends here
