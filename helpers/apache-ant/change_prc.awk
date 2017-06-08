# HOW-TO: call the program with the option '-v to=Prc2' or '-v to=Prc3'
#
# ex. if called with the option '-v to=Prc2'
# uncomments the lines starting with <!--Prc2-->
# and comments the lines starting with <!--Prc3-->

BEGIN { 
	if (to == "Prc2") { from = "Prc3" }
	else if (to == "Prc3") { from = "Prc2" }
	else {
		print "call the program with the option '-v to=Prc2' or '-v to=Prc3'"
		exit
	}
	p_to = "^<!--" to "-->$"
	p_from = "^<!--" from "-->$"
}

{ flag = 0 }

# make sure the second field is a comment
$1 ~ p_to && $2 ~ /<!--/ {
	# also print the leading whitespace to preserve formatting
	w_space = match($0, /^[ \t]*/)
	print substr($0, RSTART, RLENGTH), $1, $3
	flag = 1
}

# make sure the second field is not a comment 
$1 ~ p_from && $2 !~ /<!--/ {
	# also print the leading whitespace to preserve formatting
	w_space = match($0, /^[ \t]*/)
	print substr($0, RSTART, RLENGTH), $1, "<!--", $2, "-->"
	flag = 1
}

flag == 0 { print } # default action
