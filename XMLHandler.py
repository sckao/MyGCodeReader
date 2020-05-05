import sys
from xml.etree import ElementTree as et

def perf_func(elem, func, level=0):
    func(elem, level)
    for child in elem:
        perf_func(child, func, level + 1)

def print_level(elem, level):
    print( '-' * level + elem.tag + " = " + str(level) )


def get_level( elem, level = 0  ) :

    max_level = level
    for child in elem :
        child_level =  get_level(child,level+1)
        if child_level > max_level :
            max_level = child_level

    return max_level


class XMLHandler:

    def __init__(self):

        self.name = ''
        self.id = ''

        self.tree = None
        self.root = None
        self.branches = None


    def read(self, filename = 'materials.xml' ):

        doc = et.parse(filename).getroot()
        print(' root tag :%s' %(doc.tag ))

        i = 0
        for obj in doc :

            level = get_level(obj)
            print("=== Object %d === with %d " %(i, level ) )
            for it in obj.iter() :
                print( " (%s) -> %s : [%s]" %( it.tag, it.attrib, it.text ))

            i = i+1

        for obj in doc.findall('object') :

            print( " obj attrib name = %s" %( obj.attrib['name'] ))
            if obj.attrib['name'] != 'viscosity' :
                continue

            print(" viscos = %s" %(obj.text ))
            #print( "Obj (%s, %s) "  %( obj[0][0].text, obj[0][1].text ))
            for it in obj :
                print( "item (%s) "  %( it.tag ))


    def getRoot(self, filename ):
        self.tree = et.parse(filename)
        self.root = self.tree.getroot()

    # element is the XML element, which is a branch
    # id is the attrib dictionary
    def matchElement(self, elem, id = {} ):

        keylist = list( id.keys() )
        vallist = list( id.values() )

        #print( 'elem attribe == ' )
        #print( elem.attrib )
        match = True
        for i in range( len(keylist) ) :
            print( " [%s] <-> %s"  %( elem.attrib[keylist[i]] , vallist[i]))
            if elem.attrib[ keylist[i] ] != vallist[i]  :
                match = False

        return match


    # elemV is the list of xml elements, [ elem1, elem2, .... ]
    # branchName is the tag of the elem,
    # id is the attrib dictionary for matching the element
    def getBranches(self, elemV,  branchName, id = {} ):

        # collect the one with same tag
        theBranches = []
        for elem in elemV :
            theBranches = elem.findall(branchName )

        keylist = list( id.keys() )
        vallist = list( id.values() )

        # match them with right attrib
        selectedV = []
        for br in theBranches :

            match = self.matchElement(br, id)
            if match is True :
                selectedV.append(br)

        print(' Get %d braches ' %(len(selectedV)))
        return selectedV

    def getBranchFromRoot(self, branchNames, attrib={} ):

        bnamelist = branchNames.split(".")

        elemV = [ self.root ]
        for i in range( len( bnamelist ) ) :
            print(' branchName [%d] = %s' %(i, bnamelist[i]) )

            if i == len(bnamelist) -1 :
                elemV = self.getBranches( elemV, bnamelist[i], attrib )
            else :
                elemV = self.getBranches( elemV, bnamelist[i] )
            print( ' found %d branches  : %s ' %(len(elemV), elemV[0].tag ))

        return elemV

    # type : F(float), S(string), T(tuple), attrib is the additional attrib if specified
    #def getParameter(self, branchNames, dname = '', dtype = 'F', attrib = {} ):
    def getParameter(self, theBranch, dname = '', dtype = 'F', attrib = {} ):

        #print(" Collect Branch size = %d" %( len(elemV) ) )
        elemV = theBranch
        data = []
        for i in range( len(elemV) ) :
            print(' - branch [%d] = %s' %(i, elemV[i].tag ) )

            # add name and type in attrib for matching if specified
            #print( ' ## match attrib , name(%s) , type(%s)' %( dname, dtype))
            print( attrib.keys() )
            if dname != '' :
                attrib['name'] = dname
            if dtype != '' :
                attrib['type'] = dtype

            #print( ' ### match attrib')
            print( attrib.keys() )
            match = self.matchElement( elemV[i], attrib )
            if match and dtype == 'T' :
                data = elemV[i].text.split(',')
                print( ' - found tuple %d branches ' %(len(elemV)))
            if match and dtype == 'F' :
                data = float(elemV[i].text)
                print( ' - found float %d branches ' %(len(elemV)))
            if match :
                data = elemV[i].text
                print( ' - found String %d branches ' %(len(elemV)))

        return data

    # type : F(float), S(string), T(tuple), attrib is the additional attrib if specified
    def getParameterSet(self, branchNames, attrib = {} ):

        branchname = branchNames.split(".")

        # Find the end branch
        elemV = [ self.root ]
        for i in range( len(branchname) ) :
            print(' branchName [%d] = %s' %(i, branchname[i]) )

            elemV = self.getBranches( elemV, branchname[i] )
            print( ' found %d branches  : %s ' %(len(elemV), elemV[0].tag ))

        print(" Collect Branch size = %d" %( len(elemV) ) )
        dataV = []
        for i in range( len(elemV) ) :
            print(' - branch [%d] = %s' %(i, elemV[i].tag ) )

            match = self.matchElement( elemV[i], attrib )
            if match and elemV[i].attrib['type'] == 'T' :
                data = elemV[i].text.split(',')
                dataV.append(data)
                print( ' - found tuple %d branches ' %(len(elemV)))
            if match and elemV[i].attrib['type'] == 'F' :
                data = float(elemV[i].text)
                dataV.append(data)
                print( ' - found float %d branches ' %(len(elemV)))
            if match and elemV[i].attrib['type'] == 'S' :
                data = elemV[i].text
                dataV.append(data)
                print( ' - found String %d branches ' %(len(elemV)))

        return dataV


    def updateParameter(self, theBranch, branchname, newVal, attrib = {} ):

        for i in range( len(theBranch) ) :
            print(' - branch [%d] = %s' %(i, theBranch[i].tag ) )

            # add name and type in attrib for matching if specified
            #print( ' ## match attrib , name(%s) , type(%s)' %( dname, dtype))

            if branchname != '' :
                attrib['name'] = branchname

            #print( ' ### match attrib')
            print( attrib.keys() )

            match = self.matchElement( theBranch[i], attrib )

            if match :
                theBranch[i].text = newVal


    def write_xml(self, filename, path = 'config/' ):

        path_file_name = path + filename + '.xml'
        self.tree.write( path_file_name , "UTF-8", True )

xh = XMLHandler()
#xh.read()

xh.getRoot("materials.xml")

branches = xh.getBranchFromRoot( 'object.parameters.category', {'name':'Attributes' } )
print(' branches2 size %d ' %(len(branches)))

#branches = xh.getBranches( [xh.root], 'object' )
#branches = xh.getBranches( branches, 'parameters' )
#branches = xh.getBranches( branches, 'category', {'name':'Attributes' } )
branches = xh.getBranches( branches, 'setting' )
print(' $$ Get Branches %d - %s' %(len(branches), branches[0].tag ))
#xh.branches = branches
data = xh.getParameter( branches, 'viscosity', '' )

xh.updateParameter( branches, 'viscosity', '28'  )
xh.write_xml( 'wtest')

dataV = xh.getParameterSet( 'newObject.item1.data' )
print( ' data  ' )
print( data )
print( ' data V ' )
print( dataV )

