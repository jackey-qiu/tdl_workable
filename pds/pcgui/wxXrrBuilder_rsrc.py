data = {'application':{'type':'Application',
          'name':'Template',
    'backgrounds': [
    {'type':'Background',
          'name':'bgTemplate',
          'title':'XRR Model Builder',
          'size':(893, 717),
          'style':['resizeable'],

        'menubar': {'type':'MenuBar',
         'menus': [
             {'type':'Menu',
             'name':'menuFile',
             'label':'&File',
             'items': [
                  {'type':'MenuItem',
                   'name':'menuFileExit',
                   'label':'E&xit',
                  },
              ]
             },
             {'type':'Menu',
             'name':'menuHelp',
             'label':u'Help',
             'items': [
                  {'type':'MenuItem',
                   'name':'menuHelpParams',
                   'label':u'Help on parameters',
                  },
              ]
             },
         ]
     },
         'components': [

{'type':'Button', 
    'name':'UpdateShell', 
    'position':(20, 7), 
    'size':(82, -1), 
    'label':'Shell Update', 
    },

{'type':'Button', 
    'name':'NewModel', 
    'position':(20, 39), 
    'size':(81, 27), 
    'label':'New Model', 
    },

{'type':'ComboBox', 
    'name':'Grp', 
    'position':(254, 6), 
    'size':(116, -1), 
    'items':[], 
    },

{'type':'ComboBox', 
    'name':'Model', 
    'position':(429, 5), 
    'size':(117, -1), 
    'items':[], 
    },

{'type':'TextField', 
    'name':'SaveName', 
    'position':(206, 42), 
    'size':(141, 23), 
    },

{'type':'TextField', 
    'name':'SlabDelta', 
    'position':(486, 41), 
    'size':(58, -1), 
    'text':'10.0', 
    },

{'type':'Button', 
    'name':'SaveModel', 
    'position':(568, 41), 
    'size':(86, 25), 
    'label':'Save/Slabify', 
    },

{'type':'Button', 
    'name':'LayerInsert', 
    'position':(10, 168), 
    'size':(76, 22), 
    'label':'Insert', 
    },

{'type':'Button', 
    'name':'LayerDelete', 
    'position':(10, 199), 
    'size':(76, 22), 
    'label':'Delete', 
    },

{'type':'Button', 
    'name':'LayerMoveUp', 
    'position':(10, 228), 
    'size':(76, 22), 
    'label':'Move Up', 
    },

{'type':'Button', 
    'name':'LayerMoveDown', 
    'position':(10, 262), 
    'size':(76, 22), 
    'label':'Move Down', 
    },

{'type':'TextField', 
    'name':'LayerEdit', 
    'position':(95, 105), 
    'size':(48, -1), 
    'editable':False, 
    },

{'type':'TextField', 
    'name':'CompEdit', 
    'position':(154, 105), 
    'size':(406, -1), 
    },

{'type':'TextField', 
    'name':'ThickEdit', 
    'position':(567, 105), 
    },

{'type':'TextField', 
    'name':'DensityEdit', 
    'position':(678, 105), 
    'size':(94, -1), 
    },

{'type':'TextField', 
    'name':'RoughEdit', 
    'position':(785, 105), 
    'size':(76, -1), 
    },

{'type':'MultiColumnList', 
    'name':'LayerList', 
    'position':(93, 136), 
    'size':(784, 154), 
    'backgroundColor':(255, 255, 255), 
    'columnHeadings':[u'Layer', u'Composition                                   ', u'Thickness', u'Density', u'Roughness'], 
    'font':{'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 8}, 
    'items':[], 
    'maxColumns':20, 
    'rules':True, 
    },

{'type':'Button', 
    'name':'CalcR', 
    'position':(141, 303), 
    'size':(60, 24), 
    'label':'Calc R', 
    },

{'type':'Button', 
    'name':'CalcFY', 
    'position':(215, 303), 
    'size':(60, 24), 
    'label':'CalcFY', 
    },

{'type':'CheckBox', 
    'name':'PlotDensity', 
    'position':(33, 337), 
    'label':'Plot Density', 
    },

{'type':'CheckBox', 
    'name':'PlotComps', 
    'position':(33, 360), 
    'label':'Plot Comps', 
    },

{'type':'CheckBox', 
    'name':'PlotElements', 
    'position':(33, 381), 
    'label':'Plot Elements', 
    },

{'type':'CheckBox', 
    'name':'PlotRFY', 
    'position':(152, 337), 
    'checked':True, 
    'label':'Plot R/FY', 
    },

{'type':'CheckBox', 
    'name':'BarPlot', 
    'position':(152, 360), 
    'label':'Bar Plots', 
    },

{'type':'CheckBox', 
    'name':'PlotFracs', 
    'position':(152, 381), 
    'label':'Plot Frac', 
    },

{'type':'CheckBox', 
    'name':'HoldRFY', 
    'position':(256, 337), 
    'label':'Hold ', 
    },

{'type':'CheckBox', 
    'name':'PlotData', 
    'position':(256, 360), 
    'label':'Plot Data', 
    },

{'type':'CheckBox', 
    'name':'ShowTime', 
    'position':(256, 381), 
    'label':'Show calc time', 
    },

{'type':'Button', 
    'name':'DataUpdate', 
    'position':(496, 300), 
    'size':(52, 22), 
    'label':'Update', 
    },

{'type':'ComboBox', 
    'name':'Theta', 
    'position':(582, 326), 
    'size':(241, -1), 
    'items':[], 
    'text':'num.arange(0.01,1.01,0.01)', 
    },

{'type':'ComboBox', 
    'name':'RData', 
    'position':(582, 355), 
    'size':(241, -1), 
    'items':[], 
    },

{'type':'ComboBox', 
    'name':'FYData', 
    'position':(582, 383), 
    'size':(241, -1), 
    'items':[], 
    },

{'type':'TextField', 
    'name':'Energy', 
    'position':(190, 452), 
    'text':'10000.', 
    },

{'type':'TextField', 
    'name':'ConvWidth', 
    'position':(190, 478), 
    'text':'0.02', 
    },

{'type':'TextField', 
    'name':'SampLen', 
    'position':(190, 504), 
    'text':'50', 
    },

{'type':'TextField', 
    'name':'BeamVert', 
    'position':(190, 532), 
    'text':'0.01', 
    },

{'type':'TextField', 
    'name':'BeamHorz', 
    'position':(190, 560), 
    'text':'10.0', 
    },

{'type':'Choice', 
    'name':'AreaFlag', 
    'position':(190, 586), 
    'size':(52, -1), 
    'items':[u'0.0', u'1.0'], 
    'stringSelection':'0.0', 
    },

{'type':'TextField', 
    'name':'RefScale', 
    'position':(190, 612), 
    'text':'1.0', 
    },

{'type':'TextField', 
    'name':'FyEl', 
    'position':(672, 452), 
    'text':'0.0', 
    },

{'type':'TextField', 
    'name':'FyEnergy', 
    'position':(672, 478), 
    'text':'6000.', 
    },

{'type':'TextField', 
    'name':'DetAngle', 
    'position':(672, 504), 
    'text':'90.0', 
    },

{'type':'TextField', 
    'name':'ThetaNorm', 
    'position':(672, 532), 
    'text':'1.0', 
    },

{'type':'Choice', 
    'name':'RoughFlag', 
    'position':(672, 560), 
    'size':(68, -1), 
    'items':[u'0.0', u'1.0'], 
    'stringSelection':'1.0', 
    },

{'type':'TextField', 
    'name':'DelZ', 
    'position':(672, 586), 
    'text':'10.0', 
    },

{'type':'TextField', 
    'name':'PDepth', 
    'position':(672, 612), 
    'text':'3.0', 
    },

{'type':'StaticText', 
    'name':'FYDataLabel', 
    'position':(441, 387), 
    'text':'Fluorescent Yield Data', 
    },

{'type':'StaticText', 
    'name':'RefDataLabel', 
    'position':(441, 359), 
    'text':'Reflectivity Data', 
    },

{'type':'StaticText', 
    'name':'DataLabel', 
    'position':(427, 299), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 11}, 
    'text':'Data', 
    },

{'type':'StaticText', 
    'name':'CalcPlotLabel', 
    'position':(11, 304), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 11}, 
    'text':'Calc/Plot', 
    },

{'type':'StaticLine', 
    'name':'StaticLine9', 
    'position':(12, 294), 
    'size':(867, 4), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine8', 
    'position':(419, 299), 
    'size':(3, 109), 
    'layout':'horizontal', 
    },

{'type':'StaticText', 
    'name':'TitleText', 
    'position':(698, 8), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 12}, 
    'text':'Xray Reflectivity', 
    },

{'type':'StaticText', 
    'name':'TitleText2', 
    'position':(712, 37), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 12}, 
    'text':'Model Builder', 
    },

{'type':'StaticText', 
    'name':'ReadLabel', 
    'position':(125, 10), 
    'text':'Read Model:', 
    },

{'type':'StaticText', 
    'name':'GrpLabel', 
    'position':(207, 9), 
    'text':'Group', 
    },

{'type':'StaticText', 
    'name':'ModelLabel', 
    'position':(380, 8), 
    'text':'Model', 
    },

{'type':'StaticText', 
    'name':'SaveModelLabel', 
    'position':(124, 46), 
    'text':'Save Model:', 
    },

{'type':'StaticText', 
    'name':'SlabDeltaLabel', 
    'position':(365, 46), 
    'text':'Slab Delta Z (ang)', 
    },

{'type':'StaticText', 
    'name':'LayerTitleText', 
    'position':(12, 79), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 11}, 
    'text':'Layers', 
    },

{'type':'StaticText', 
    'name':'LayerText', 
    'position':(103, 87), 
    'text':'Layer', 
    },

{'type':'StaticText', 
    'name':'CompText', 
    'position':(325, 86), 
    'text':'Composition', 
    },

{'type':'StaticText', 
    'name':'ThicknessText', 
    'position':(569, 84), 
    'text':'Thickness (ang)', 
    },

{'type':'StaticText', 
    'name':'DensityText', 
    'position':(674, 83), 
    'text':'Density (g/cm^3)', 
    },

{'type':'StaticText', 
    'name':'RoughnessText', 
    'position':(781, 82), 
    'text':'Roughness (ang)', 
    },

{'type':'StaticText', 
    'name':'ParamLabel', 
    'position':(11, 420), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 12}, 
    'text':'Parameters', 
    },

{'type':'StaticText', 
    'name':'ThetaLabel', 
    'position':(441, 330), 
    'text':'Theta (deg)', 
    },

{'type':'StaticText', 
    'name':'EnergyLabel', 
    'position':(39, 456), 
    'text':'Energy (eV)', 
    },

{'type':'StaticText', 
    'name':'ConvWidthLabel', 
    'position':(39, 482), 
    'text':'Convolution Width (deg)', 
    },

{'type':'StaticText', 
    'name':'SampleLenLabel', 
    'position':(39, 508), 
    'text':'Sample Length (mm)', 
    },

{'type':'StaticText', 
    'name':'BeamVertLabel', 
    'position':(39, 536), 
    'text':'Beam Vert (mm)', 
    },

{'type':'StaticText', 
    'name':'BeamHorzLabel', 
    'position':(39, 564), 
    'text':'Beam Horz (mm)', 
    },

{'type':'StaticText', 
    'name':'AreaFlagLabel', 
    'position':(39, 590), 
    'text':'Model Area Variation ', 
    },

{'type':'StaticText', 
    'name':'RefScaleLabel', 
    'position':(39, 616), 
    'text':'Reflectivity Scale', 
    },

{'type':'StaticText', 
    'name':'FyIdxLabel', 
    'position':(467, 456), 
    'text':'FY Element (symbol or Z)', 
    },

{'type':'StaticText', 
    'name':'FyEnergyLabel', 
    'position':(467, 482), 
    'text':'FY Energy (eV or line)', 
    },

{'type':'StaticText', 
    'name':'DetAngleLabel', 
    'position':(467, 508), 
    'text':'FY Detector Angle (deg)', 
    },

{'type':'StaticText', 
    'name':'TextNormLabel', 
    'position':(467, 536), 
    'text':'FY Normalization Angle (deg)', 
    },

{'type':'StaticText', 
    'name':'RoughFlagLabel', 
    'position':(467, 564), 
    'text':'RoughnessFlag', 
    },

{'type':'StaticText', 
    'name':'DelZLabel', 
    'position':(467, 590), 
    'text':'Integration Delta Z (ang)', 
    },

{'type':'StaticText', 
    'name':'PDepthLabel', 
    'position':(467, 616), 
    'text':'FY Base Penetration Depth Factor', 
    },

{'type':'StaticLine', 
    'name':'StaticLine7', 
    'position':(419, 438), 
    'size':(3, 196), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine6', 
    'position':(11, 643), 
    'size':(864, 4), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine5', 
    'position':(681, 3), 
    'size':(3, 65), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine4', 
    'position':(121, 34), 
    'size':(556, 5), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine3', 
    'position':(111, 5), 
    'size':(3, 66), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine2', 
    'position':(11, 416), 
    'size':(863, 4), 
    'layout':'horizontal', 
    },

{'type':'StaticLine', 
    'name':'StaticLine1', 
    'position':(9, 71), 
    'size':(858, 3), 
    'layout':'horizontal', 
    },

] # end components
} # end background
] # end backgrounds
} }
