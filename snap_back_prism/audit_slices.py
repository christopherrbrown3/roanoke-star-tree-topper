"""Compare actual local slices against the committed one-piece baseline."""
import hashlib
import json
from pathlib import Path
import re
import sys

H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'pentagrammic_prism'))
from audit_slices import audit

def seconds(time):
    units={'d':86400,'h':3600,'m':60,'s':1}
    return sum(int(n)*units[u] for n,u in re.findall(r'(\d+)([dhms])',time))

if __name__=='__main__':
    report={}
    for key,filename in [('front','front_shell_A1.3mf'),('back','snap_back_A1.3mf'),
                         ('sample','connector_sample_A1.3mf')]:
        gcode=H/'slicer_check'/(key+'.gcode')
        if not gcode.exists(): continue
        r=audit(H/filename,gcode)
        assert r['settings']['enable_support']=='0'
        tools=[]; selected_layers=[]; layer_z=0.
        with gcode.open() as stream:
            for line in stream:
                if line.startswith('; Z_HEIGHT: '): layer_z=float(line.split(':',1)[1])
                match=re.fullmatch(r'T([01])',line.partition(';')[0].strip())
                if match:
                    tools.append(int(match.group(1)))
                    selected_layers.append(layer_z)
        r['tool_selection_sequence_count']=len(tools)
        r['tool_changes']=sum(a!=b for a,b in zip(tools,tools[1:]))
        r['tool_selection_layer_z_mm']=selected_layers
        r['total_estimated_seconds']=seconds(r['total_estimated_time'])
        report[key]=r
    if {'front','back'}.issubset(report):
        baseline=json.loads((H.parent/'pentagrammic_prism/slicer_validation.json').read_text())['two_color']
        total_seconds=report['front']['total_estimated_seconds']+report['back']['total_estimated_seconds']
        total_g=round(report['front']['total_filament_g']+report['back']['total_filament_g'],2)
        report['comparison']={'baseline_commit':'fcb757d','baseline_time':baseline['total_estimated_time'],
          'baseline_filament_g':baseline['total_filament_g'],'snap_back_total_seconds':total_seconds,
          'snap_back_total_filament_g':total_g,
          'time_reduction_percent':round(100*(1-total_seconds/seconds(baseline['total_estimated_time'])),1),
          'filament_reduction_percent':round(100*(1-total_g/baseline['total_filament_g']),1),
          'sample_excluded_from_topper_total':True}
    (H/'slicer_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    geometry=json.loads((H/'mesh_validation.json').read_text())
    for key,filename in [('front','front_shell_A1.3mf'),('back','snap_back_A1.3mf'),('sample','connector_sample_A1.3mf')]:
        if key in report:
            assert geometry['packages'][filename]['sha256']==report[key]['package_sha256']
            geometry['packages'][filename]['GUI_slice_complete']=True
    (H/'mesh_validation.json').write_text(json.dumps(geometry,indent=2)+'\n')
    print(json.dumps(report,indent=2))
