
nano request-xmlrpc-sample.xml # copy as content the .xml in below examples
curl -v --request POST --header "Content-Type: text/xml" --data @request-xmlrpc-sample.xml http://localhost:8069/xmlrpc/2/common

# == Examples of .xml file content ==

# 1: get Odoo version
<?xml version='1.0'?>
<methodCall>
    <methodName>version</methodName>
    <params></params>
</methodCall>

# 2: authenticate a user (get UID)
<?xml version='1.0'?>
<methodCall>
    <methodName>authenticate</methodName>
    <params>
        <param> <value><string>o18-flavigny-staging</string></value> </param> <!-- database -->
        <param> <value><string>admin</string></value> </param <!-- user -->
        <param> <value><string>admin</string></value> </param> <!-- api key or password -->
        <param> <value><struct> </struct></value> </param>
    </params>
</methodCall>

# 3: call `execute_kw` XML-RPC method to execute an Odoo exposed python method
<?xml version='1.0'?>
<methodCall>
    <methodName>execute_kw</methodName>
    <params>
        <param> <value><string>o18-flavigny-staging</string></value> </param> <!-- database -->
        <param> <value><int>2</int></value> </param> <!-- uid -->
        <param> <value><string>admin</string></value> </param> <!-- api key or password -->
        <param> <value><string>res.partner</string></value> </param> <!-- Odoo model -->
        <param> <value><string>search_read</string></value> </param> <!-- Odoo python exposed method -->
        <param> <value>
            <array>
             <data>
              <value>
               <array>
                <data>
                 <value>
                  <array>
                   <data>
                    <!-- this is an Odoo domain, equivalent to SQL `WHERE is_company = 1` -->
                    <value> <string>is_company</string> </value>
                    <value> <string>=</string> </value>
                    <value> <boolean>1</boolean> </value>
                   </data>
                  </array>
                 </value>
                </data>
               </array>
              </value>
             </data>
            </array>
        </value> </param>
        <param>
        <value>
         <struct>
          <member>
           <name>offset</name>
           <value><int>0</int></value>
          </member>
          <member>
           <name>fields</name>
            <value>
             <array>
              <data>
               <value><string>name</string></value>
               <value><string>email</string></value>
               <value><string>phone</string></value>
              </data>
             </array>
            </value>
          </member>
          <member>
           <name>limit</name>
           <value><int>5</int></value>
          </member>
         </struct>
        </value> </param>
    </params>
</methodCall>
