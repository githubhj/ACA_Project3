#include "MOSI_protocol.h"
#include "../sim/mreq.h"
#include "../sim/sim.h"
#include "../sim/hash_table.h"

extern Simulator *Sim;

/*************************
 * Constructor/Destructor.
 *************************/
MOSI_protocol::MOSI_protocol (Hash_table *my_table, Hash_entry *my_entry)
    : Protocol (my_table, my_entry)
{
	// Initialize lines to not have the data yet!
	this->state = MOSI_CACHE_I;
}

MOSI_protocol::~MOSI_protocol ()
{    
}

void MOSI_protocol::dump (void)
{
    const char *block_states[5] = {"X","I","S","O","M"};
    fprintf (stderr, "MOSI_protocol - state: %s\n", block_states[state]);
}

void MOSI_protocol::process_cache_request (Mreq *request)
{
	switch (state) {
	case MOSI_CACHE_I:  do_cache_I (request); break;
	case MOSI_CACHE_S:  do_cache_S (request); break;
	case MOSI_CACHE_O:  do_cache_O (request); break;
	case MOSI_CACHE_M:  do_cache_M (request); break;
	case MOSI_CACHE_IM: do_cache_IM (request); break;
	case MOSI_CACHE_IS: do_cache_IS (request); break;
	case MOSI_CACHE_SM: do_cache_SM (request); break;
	case MOSI_CACHE_OM: do_cache_OM (request); break;

    default:
        fatal_error ("Invalid Cache State for MOSI Protocol\n");
    }
}

void MOSI_protocol::process_snoop_request (Mreq *request)
{
	switch (state) {
	case MOSI_CACHE_I:  do_snoop_I (request); break;
	case MOSI_CACHE_S:  do_snoop_S (request); break;
	case MOSI_CACHE_O:  do_snoop_O (request); break;
	case MOSI_CACHE_M:  do_snoop_M (request); break;
	case MOSI_CACHE_IM: do_snoop_IM (request); break;
	case MOSI_CACHE_IS: do_snoop_IS (request); break;
	case MOSI_CACHE_SM: do_snoop_SM (request); break;
	case MOSI_CACHE_OM: do_snoop_OM (request); break;

    default:
    	fatal_error ("Invalid Cache State for MOSI Protocol\n");
    }
}

inline void MOSI_protocol::do_cache_I (Mreq *request)
{
	switch (request->msg) {
	// If we get a request from the processor we need to get the data
	case LOAD:
		send_GETS(request->addr);
		/*Change state to IS*/
		state = MOSI_CACHE_IS;
		/* This is a cache miss */
		Sim->cache_misses++;
		break;
	case STORE:
		/* Line up the GETM in the Bus' queue */
		send_GETM(request->addr);
		state = MOSI_CACHE_IM;
		/* This is a cache miss */
		Sim->cache_misses++;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: I state shouldn't see this message\n");
	}

}

inline void MOSI_protocol::do_cache_S (Mreq *request)
{
	switch (request->msg) {
	/* The S state means we have the data in a shared state and we can modify it after invalidating it on the bus with GETM.  Therefore any request
	 * from the processor (read or write) can be immediately satisfied.
	 */
	case LOAD:
		// This is how you send data back to the processor to finish the request
		// Note: There was no need to send anything on the bus on a hit.
		send_DATA_to_proc(request->addr);
		//Keep the state same to S
		state = MOSI_CACHE_S;
		break;
	case STORE:
		send_GETM(request->addr);
		state = MOSI_CACHE_SM;
		Sim->cache_misses++;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: S state shouldn't see this message\n");
	}

}

inline void MOSI_protocol::do_cache_O (Mreq *request)
{
	switch (request->msg) {
	/* The S state means we have the data in a shared state and we can modify it after invalidating it on the bus with GETM.  Therefore any request
	 * from the processor (read or write) can be immediately satisfied.
	 */
	case LOAD:
		// This is how you send data back to the processor to finish the request
		// Note: There was no need to send anything on the bus on a hit.
		send_DATA_to_proc(request->addr);
		state = MOSI_CACHE_O;
		break;
	case STORE:

		send_GETM(request->addr);
		state = MOSI_CACHE_OM;
		Sim->cache_misses++;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: S state shouldn't see this message\n");
	}

}

inline void MOSI_protocol::do_cache_M (Mreq *request)
{
	switch (request->msg) {
	/* The M state means we have the data and we can modify it.  Therefore any request
	 * from the processor (read or write) can be immediately satisfied.
	 */
	case LOAD:
	case STORE:
		// This is how you send data back to the processor to finish the request
		// Note: There was no need to send anything on the bus on a hit.
		send_DATA_to_proc(request->addr);
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: M state shouldn't see this message\n");
	}

}

inline void MOSI_protocol::do_cache_IM (Mreq *request)
{
	switch (request->msg) {
	/* If the block is in the IM state that means it sent out a GET message
	 * and is waiting on DATA.  Therefore the processor should be waiting
	 * on a pending request. Therefore we should not be getting any requests from
	 * the processor.
	 */
	case LOAD:
	case STORE:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error("Should only have one outstanding request per processor!");
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_cache_IS (Mreq *request)
{
	switch (request->msg) {
	/* If the block is in the IM state that means it sent out a GET message
	 * and is waiting on DATA.  Therefore the processor should be waiting
	 * on a pending request. Therefore we should not be getting any requests from
	 * the processor.
	 */
	case LOAD:
	case STORE:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error("Should only have one outstanding request per processor!");
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_cache_SM (Mreq *request)
{
	switch (request->msg) {
	/* If the block is in the IM state that means it sent out a GET message
	 * and is waiting on DATA.  Therefore the processor should be waiting
	 * on a pending request. Therefore we should not be getting any requests from
	 * the processor.
	 */
	case LOAD:
	case STORE:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error("Should only have one outstanding request per processor!");
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_cache_OM (Mreq *request)
{
	switch (request->msg) {
	/* If the block is in the IM state that means it sent out a GET message
	 * and is waiting on DATA.  Therefore the processor should be waiting
	 * on a pending request. Therefore we should not be getting any requests from
	 * the processor.
	 */
	case LOAD:
	case STORE:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error("Should only have one outstanding request per processor!");
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}



inline void MOSI_protocol::do_snoop_I (Mreq *request)
{
	switch (request->msg) {
	case GETS:
	case GETM:
	case DATA:
		/**
		 * If we snoop a message from another cache and we are in I, then we don't
		 * need to do anything!  We obviously cannot supply data since we don't have
		 * it, and we don't need to downgrade our state since we are already in I.
		 */
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: I state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_S (Mreq *request)
{
	switch (request->msg) {
	case GETS:
		//set_shared_line();
		state = MOSI_CACHE_S;
		break;
	case GETM:
		set_shared_line();
		state = MOSI_CACHE_I;
		break;
	case DATA:
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: S state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_O (Mreq *request)
{
	switch (request->msg) {
	case GETS:
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		state = MOSI_CACHE_O;
		break;
	case GETM:
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		state = MOSI_CACHE_I;
		break;
	case DATA:
		fatal_error ("Should not see data for this line!  I have the line!");
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: E state shouldn't see this message\n");
	}

}

inline void MOSI_protocol::do_snoop_M (Mreq *request)
{
	switch (request->msg) {
	case GETS:
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		state = MOSI_CACHE_O;
		break;
	case GETM:
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		state = MOSI_CACHE_I;
		break;
	case DATA:
		fatal_error ("Should not see data for this line!  I have the line!");
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: M state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_IM (Mreq *request)
{
	switch (request->msg) {
	case GETS:
	case GETM:
		/** While in IM we will see our own GETS or GETM on the bus.  We should just
		 * ignore it anSd wait for DATA to show up.
		 */
		break;
	case DATA:
		send_DATA_to_proc(request->addr);
		state = MOSI_CACHE_M;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_IS (Mreq *request)
{
	switch (request->msg) {
	case GETS:
	case GETM:
		/** While in IM we will see our own GETS or GETM on the bus.  We should just
		 * ignore it anSd wait for DATA to show up.
		 */
		break;
	case DATA:
		send_DATA_to_proc(request->addr);
		state = MOSI_CACHE_S;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_SM (Mreq *request)
{
	switch (request->msg) {
	case GETS:
	case GETM:
		/** While in IM we will see our own GETS or GETM on the bus.  We should just
		 * ignore it anSd wait for DATA to show up.
		 */
		break;
	case DATA:
		send_DATA_to_proc(request->addr);
		state = MOSI_CACHE_M;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: SM state shouldn't see this message\n");
	}
}

inline void MOSI_protocol::do_snoop_OM (Mreq *request)
{
	switch (request->msg) {
	case GETS:
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		break;
	case GETM:
		/** While in IM we will see our own GETS or GETM on the bus.  We should just
		 * ignore it anSd wait for DATA to show up.
		 */
		set_shared_line();
		send_DATA_on_bus(request->addr,request->src_mid);
		state = MOSI_CACHE_IM;
		break;
	case DATA:
		send_DATA_to_proc(request->addr);
		state = MOSI_CACHE_M;
		break;
	default:
		request->print_msg (my_table->moduleID, "ERROR");
		fatal_error ("Client: IM state shouldn't see this message\n");
	}
}


