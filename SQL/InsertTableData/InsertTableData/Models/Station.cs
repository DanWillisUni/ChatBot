using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text;

namespace InsertTableData.Models
{
    public class Station
    {
        public string name { get; set; }
        [DisplayName("longname.name_alias")]
        public string longname { get; set; }
        public string alpha3 { get; set; }
        public string tiploc { get; set; }
        public string column5 { get; set; }

        public override string ToString()
        {
            string column5R = column5 == "" || column5 == null ? "\\N" : column5;
            return $"{name},{longname},{alpha3},{tiploc},{column5R}".Replace("'","''").Replace("\"","'").Replace("\\N","null");
        }

    }
}
