EXAMPLE_FOLDER="./example"
EXAMPLE_PDB_FOLDER="$EXAMPLE_FOLDER/pdbs"
EXAMPLE_PROCESSED_FOLDER="$EXAMPLE_FOLDER/processed"
EXAMPLE_RESULTS_FOLDER="$EXAMPLE_FOLDER/search_results"




run (){
	sudo docker run -it -v $PWD:/home/masif-neosurf masif-neosurf
}



process-list (){
	path=$(realpath $1)
	echo "Processing CODES in : $path"

	declare -a codes=()
	while read -d "," line; do
		echo $line
		process-pdb $line
	done < $path
}

process-pdb (){
	CODE=$1
	FNAME="$1.pdb"
	CHAIN="$2"
	mkdir -p $EXAMPLE_PDB_FOLDER
	FILEPATH="$EXAMPLE_PDB_FOLDER/$FNAME"



	if ! [[ -f "$FILEPATH" ]]; then
		curl https://files.rcsb.org/download/${CODE}.pdb -o "$FILEPATH" || return 1
	fi

	if [[ -z "$CHAIN" ]]; then
		echo "Processing ${CODE} (all chains)"
		declare -a chains=()
		while read -r line; do
			line=$(echo $line | tr -s ' ')
			#echo $line
			if [[ $(echo $line | cut -d " " -f1 ) == "ATOM" ]]; then
				chain="$(echo $line | cut -d " " -f5)"
				#echo "$line $chain"
				chain_added="0"
				#echo "${chains[@]}"

				#echo $(echo "${chains[@]}" | grep -c "$chain")
				#echo $([[ $(echo "${chains[@]}" | grep -c "$chain") -gt 0 ]])

				if [[ $(echo "${chains[@]}" | grep -c "$chain") -eq 0 ]]; then
					echo "- Detected new chain: $chain"
					chains+=("$chain")
				fi

			fi
		done < <(grep 'ATOM ' $FILEPATH | grep "CA")
	else
		echo "Processing ${CODE}_${CHAIN}"
		declare -a chains=("$CHAIN")
	fi
	for chain in ${chains[@]}; do
		echo ""
		if [[ -d $EXAMPLE_PROCESSED_FOLDER/descriptors/sc05/all_feat/${CODE}_${CHAIN} ]]; then
			echo " * PDB (${CODE}_${CHAIN}) already processed"
		else
			echo " * Processing $FILEPATH ${CODE}_${chain}"
			python -W ignore ./preprocess_pdb.py $FILEPATH ${CODE}_${chain} -o $EXAMPLE_PROCESSED_FOLDER
		fi

	done
}



search (){
	if [[ $# -lt 2 ]]; then
		echo "Please provide chain"
		return 1
	fi

	echo ""
	echo " * Searching targets for $1_$2 in $EXAMPLE_PROCESSED_FOLDER"

	python -W ignore masif_search.py \
		--target_dir $EXAMPLE_PROCESSED_FOLDER \
		--target $1_$2 \
		--database $EXAMPLE_PROCESSED_FOLDER \
		--out_dir $EXAMPLE_RESULTS_FOLDER \
		--num_sites  4
	echo " * Results saved to $EXAMPLE_RESULTS_FOLDER"
}

